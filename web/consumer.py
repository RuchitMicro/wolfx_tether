# consumer.py

import io
import json
import logging
import threading
import time

import paramiko
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

from web.models import Host, ProjectAction

logger = logging.getLogger(__name__)


class SSHConsumer(AsyncWebsocketConsumer):
    """
    WebSocket SSH terminal + action runner.

    - No ORM/lazy loads in async without wrappers.
    - Terminal uses one SSHClient.
    - Each action uses its own SSHClient (separate session).
    """

    ssh_client = None
    ssh_channel = None
    output_thread = None
    keep_running = True
    host = None

    async def connect(self):
        host_id = self.scope['url_route']['kwargs'].get('host_id')
        if not host_id:
            await self.accept()
            await self.send_text_to_client("Error: No host ID specified.")
            await self.close()
            return

        if not getattr(self.scope.get('user'), 'is_authenticated', False):
            await self.accept()
            await self.send_text_to_client("Error: You must be authenticated to access this host.")
            await self.close()
            return

        await self.accept()

        # Load host safely
        try:
            self.host = await self.get_host(host_id)
        except Exception:
            await self.send_text_to_client("Error: Unable to fetch host details.")
            await self.close()
            return

        # Establish interactive terminal
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.host.use_credential == 'pem':
                decrypted_pem = self.host.decrypt_pem(self.host.encrypted_pem)
                if not decrypted_pem:
                    raise ValueError("Decryption of PEM file failed.")
                file_obj = io.StringIO(decrypted_pem.decode('utf-8'))
                from paramiko import Ed25519Key, RSAKey, SSHException
                try:
                    pkey = Ed25519Key.from_private_key(file_obj)
                except SSHException:
                    file_obj.seek(0)
                    pkey = RSAKey.from_private_key(file_obj)

                self.ssh_client.connect(
                    hostname=self.host.host_address,
                    port=self.host.port,
                    username=self.host.username,
                    pkey=pkey,
                    timeout=30,
                )
            elif self.host.use_credential == 'password':
                decrypted_password = self.host.decrypt_password(self.host.password)
                self.ssh_client.connect(
                    hostname=self.host.host_address,
                    port=self.host.port,
                    username=self.host.username,
                    password=decrypted_password,
                    timeout=30,
                )
            else:
                raise ValueError("Invalid credential type specified.")

            self.ssh_channel = self.ssh_client.invoke_shell(term='xterm')
            self.ssh_channel.settimeout(0.0)

            self.keep_running = True
            self.output_thread = threading.Thread(target=self.read_ssh_output, daemon=True)
            self.output_thread.start()

            logger.info(f"SSH terminal connected to {self.host.host_address} (user={self.scope['user']})")

        except Exception as e:
            logger.error(f"SSH terminal connect failed (host_id={host_id}): {e}", exc_info=True)
            await self.close()
            raise

    async def disconnect(self, close_code):
        self.keep_running = False
        try:
            if self.ssh_channel is not None:
                self.ssh_channel.close()
        except Exception:
            pass
        try:
            if self.ssh_client is not None:
                self.ssh_client.close()
        except Exception:
            pass
        logger.info(f"SSH terminal closed (user={self.scope['user']}, code={close_code})")

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        # Control channel
        try:
            message = json.loads(text_data)
            mtype = message.get('type')
            if mtype == 'input':
                data = message.get('data', '')
                if self.ssh_channel is not None:
                    try:
                        self.ssh_channel.send(data)
                    except Exception as e:
                        await self.send_text_to_client(f"\r\nError writing to SSH channel: {e}\r\n")
            elif mtype == 'kill':
                await self.kill_ssh_connection()
            elif mtype == 'run_action':
                action_id = message.get('action_id')
                await self.handle_run_action(action_id)
            else:
                await self.send_text_to_client("Error: Unknown message type.")
            return
        except json.JSONDecodeError:
            pass

        # Raw terminal input
        if self.ssh_channel is not None:
            try:
                self.ssh_channel.send(text_data)
            except Exception as e:
                await self.send_text_to_client(f"\r\nError writing to SSH channel: {e}\r\n")

    def read_ssh_output(self):
        """Read from interactive shell and forward to client."""
        while self.keep_running and self.ssh_channel is not None and not self.ssh_channel.closed:
            try:
                if self.ssh_channel.recv_ready():
                    chunk = self.ssh_channel.recv(2048)
                    if chunk:
                        async_to_sync(self.send_text_to_client)(chunk.decode('utf-8', errors='replace'))
                time.sleep(0.02)
            except Exception as e:
                logger.error(f"Terminal read error: {e}")
                break

    # DB + permission (async-safe)
    @staticmethod
    @database_sync_to_async
    def get_host(host_id):
        return get_object_or_404(Host, id=host_id)

    @staticmethod
    @database_sync_to_async
    def get_action_minimal(action_id):
        """
        Return minimal IDs only to avoid lazy relation access in async code.
        """
        pa = get_object_or_404(
            ProjectAction.objects.select_related('project__host').only(
                'id', 'project_id', 'project__host_id'
            ),
            id=action_id
        )
        return {'id': pa.id, 'project_id': pa.project_id, 'host_id': pa.project.host_id}

    @staticmethod
    @database_sync_to_async
    def user_has_perm(user, perm_codename, project_action_id=None):
        # Wrap has_perm in sync thread to avoid SynchronousOnlyOperation
        if project_action_id is not None and user.has_perm('can_run_actions', ProjectAction.objects.get(pk=project_action_id)):
            return True
        return user.has_perm(perm_codename) or user.is_superuser 


    # Send helpers
    async def send_text_to_client(self, message: str):
        await self.send(text_data=message)

    async def send_json_to_client(self, data: dict):
        await self.send(text_data=json.dumps(data))

    # Control handlers
    async def kill_ssh_connection(self):
        self.keep_running = False
        try:
            if self.ssh_channel is not None:
                self.ssh_channel.close()
        except Exception:
            pass
        try:
            if self.ssh_client is not None:
                self.ssh_client.close()
        except Exception:
            pass
        await self.send_text_to_client("\r\nSSH connection terminated by user.\r\n")
        await self.close()
        logger.info(f"SSH terminal terminated by user (user={self.scope['user']})")

    async def handle_run_action(self, action_id):
        """
        Validate and spawn an action runner thread.
        Uses only primitives in async (IDs, booleans).
        The worker creates its own SSH connection.
        """
        if not action_id:
            await self.send_json_to_client({'type': 'action_error', 'id': action_id, 'message': 'No action ID provided.'})
            return

        try:
            a = await self.get_action_minimal(action_id)

            if a['host_id'] != getattr(self.host, 'id', None):
                await self.send_json_to_client({
                    'type': 'action_denied',
                    'id': action_id,
                    'reason': 'Action does not belong to this host.'
                })
                return

            has_perm = await (self.user_has_perm(self.scope['user'], 'web.can_run_actions', a['id']))
            if not has_perm:
                await self.send_json_to_client({
                    'type': 'action_denied',
                    'id': action_id,
                    'reason': 'Insufficient permissions.'
                })
                return

            await self.send_json_to_client({'type': 'action_status', 'id': action_id, 'status': 'running'})

            threading.Thread(target=self.run_action_thread, args=(int(action_id),), daemon=True).start()

        except Exception as e:
            logger.error(f"handle_run_action error: {e}", exc_info=True)
            await self.send_json_to_client({'type': 'action_error', 'id': action_id, 'message': str(e)})

    
    # Action worker (sync thread)
    def run_action_thread(self, action_id: int):
        """
        Run the action in a separate SSH session.
        Re-fetch ORM objects synchronously in this thread.
        Streams a tail and sends final status.
        """
        action_ssh = None
        channel = None
        try:
            action = (
                ProjectAction.objects
                .select_related('project__host')
                .prefetch_related('project__secrets')
                .get(pk=action_id)
            )
            project = action.project
            host = project.host
            secrets = list(project.secrets.all())

            action_ssh = paramiko.SSHClient()
            action_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if host.use_credential == 'pem':
                decrypted_pem = host.decrypt_pem(host.encrypted_pem)
                if not decrypted_pem:
                    raise ValueError("Decryption of PEM file failed (action).")
                file_obj = io.StringIO(decrypted_pem.decode('utf-8'))
                from paramiko import Ed25519Key, RSAKey, SSHException
                try:
                    pkey = Ed25519Key.from_private_key(file_obj)
                except SSHException:
                    file_obj.seek(0)
                    pkey = RSAKey.from_private_key(file_obj)

                action_ssh.connect(
                    hostname=host.host_address,
                    port=host.port,
                    username=host.username,
                    pkey=pkey,
                    timeout=30,
                )
            elif host.use_credential == 'password':
                decrypted_password = host.decrypt_password(host.password)
                action_ssh.connect(
                    hostname=host.host_address,
                    port=host.port,
                    username=host.username,
                    password=decrypted_password,
                    timeout=30,
                )
            else:
                raise ValueError("Invalid credential type for action SSH connect.")

            transport = action_ssh.get_transport()
            if not transport or not transport.is_active():
                async_to_sync(self.send_json_to_client)({
                    'type': 'action_error',
                    'id': action_id,
                    'message': 'SSH transport is not active for action.'
                })
                return

            channel = transport.open_session()
            channel.exec_command('bash')
            stdin = channel.makefile('wb', -1)

            # Export secrets
            for s in secrets:
                val = s.decrypt_value().replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
                stdin.write(f'export {s.key}="{val}"\n'.encode('utf-8'))

            # Run commands then cleanup and exit
            stdin.write(action.commands.encode('utf-8') + b'\n')
            for s in secrets:
                stdin.write(f'unset {s.key}\n'.encode('utf-8'))
            stdin.write(b'exit\n')
            stdin.flush()
            stdin.close()

            # Live tail
            tail = []
            max_tail = 10
            while not channel.exit_status_ready():
                while channel.recv_ready():
                    part = channel.recv(4096).decode('utf-8', 'replace')
                    if part:
                        tail = (tail + part.splitlines())[-max_tail:]
                        async_to_sync(self.send_json_to_client)({
                            'type': 'action_status',
                            'id': action_id,
                            'status': 'running',
                            'tail': tail
                        })
                time.sleep(0.1)

            # Drain remaining
            remaining = b''
            while channel.recv_ready():
                remaining += channel.recv(4096)
            if remaining:
                more = remaining.decode('utf-8', 'replace')
                tail = (tail + more.splitlines())[-max_tail:]

            exit_status = channel.recv_exit_status()
            final_status = 'success' if exit_status == 0 else 'failure'

            async_to_sync(self.send_json_to_client)({
                'type': 'action_result',
                'id': action_id,
                'status': final_status,
                'tail': tail
            })

        except Exception as e:
            logger.error(f"run_action_thread error (action_id={action_id}): {e}", exc_info=True)
            async_to_sync(self.send_json_to_client)({'type': 'action_error', 'id': action_id, 'message': str(e)})
        finally:
            try:
                if channel:
                    channel.close()
            except Exception:
                pass
            try:
                if action_ssh:
                    action_ssh.close()
            except Exception:
                pass
