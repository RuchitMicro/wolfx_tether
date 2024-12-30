import io
import json
import paramiko
import threading
import time
import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.shortcuts import get_object_or_404
from web.models import Host

logger = logging.getLogger(__name__)

class SSHConsumer(AsyncWebsocketConsumer):
    ssh_client = None
    ssh_channel = None
    output_thread = None
    keep_running = True

    async def connect(self):
        host_id = self.scope['url_route']['kwargs'].get('host_id')
        if not host_id:
            await self.accept()
            await self.send_text_to_client("Error: No host ID specified.")
            await self.close()
            return

        if not self.scope['user'].is_authenticated:
            await self.accept()
            await self.send_text_to_client("Error: You must be authenticated to access this host.")
            await self.close()
            return

        await self.accept()

        try:
            host = await self.get_host(host_id)
        except Exception as e:
            await self.send_text_to_client("Error: Unable to fetch host details.")
            await self.close()
            return

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if host.use_credential == 'pem':
                decrypted_pem = host.decrypt_pem(host.encrypted_pem)
                if not decrypted_pem:
                    raise ValueError("Decryption of PEM file failed.")

                file_obj = io.StringIO(decrypted_pem.decode('utf-8'))

                # Try Ed25519 first, then RSA
                from paramiko import Ed25519Key, RSAKey, SSHException
                try:
                    pkey = Ed25519Key.from_private_key(file_obj)
                except SSHException:
                    file_obj.seek(0)
                    pkey = RSAKey.from_private_key(file_obj)

                self.ssh_client.connect(
                    hostname=host.host_address,
                    port=host.port,
                    username=host.username,
                    pkey=pkey,
                    timeout=30
                )

            elif host.use_credential == 'password':
                decrypted_password = host.decrypt_password(host.password)
                self.ssh_client.connect(
                    hostname=host.host_address,
                    port=host.port,
                    username=host.username,
                    password=decrypted_password,
                    timeout=30
                )
            else:
                raise ValueError("Invalid credential type specified.")

            self.ssh_channel = self.ssh_client.invoke_shell(term='xterm')
            self.ssh_channel.settimeout(0.0)

            self.keep_running = True
            self.output_thread = threading.Thread(target=self.read_ssh_output, daemon=True)
            self.output_thread.start()

            logger.info(f"SSH connection established to {host.host_address} by user {self.scope['user']}")

        except Exception as e:
            logger.error(f"SSH connection failed for host_id {host_id}: {str(e)}", exc_info=True)
            await self.close()
            raise

    async def disconnect(self, close_code):
        self.keep_running = False
        if self.ssh_channel is not None:
            self.ssh_channel.close()
        if self.ssh_client is not None:
            self.ssh_client.close()
        logger.info(f"SSH connection closed for user {self.scope['user']} with close_code {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                message = json.loads(text_data)
                msg_type = message.get('type')
                if msg_type == 'input':
                    data = message.get('data', '')
                    if self.ssh_channel is not None:
                        try:
                            self.ssh_channel.send(data)
                        except Exception as e:
                            await self.send_text_to_client(f"\r\nError writing to SSH channel: {str(e)}\r\n")
                elif msg_type == 'kill':
                    await self.kill_ssh_connection()
                else:
                    await self.send_text_to_client("Error: Unknown message type.")
            except json.JSONDecodeError:
                if self.ssh_channel is not None:
                    try:
                        self.ssh_channel.send(text_data)
                    except Exception as e:
                        await self.send_text_to_client(f"\r\nError writing to SSH channel: {str(e)}\r\n")

    def read_ssh_output(self):
        while self.keep_running and self.ssh_channel is not None and not self.ssh_channel.closed:
            try:
                if self.ssh_channel.recv_ready():
                    output = self.ssh_channel.recv(1024)
                    if output:
                        async_to_sync(self.send_text_to_client)(output.decode('utf-8', errors='replace'))
                time.sleep(0.02)
            except Exception as e:
                logger.error(f"Error reading from SSH channel: {str(e)}")
                break

    @staticmethod
    async def get_host(host_id):
        from asgiref.sync import sync_to_async
        return await sync_to_async(get_object_or_404)(Host, id=host_id)

    async def send_text_to_client(self, message):
        await self.send(text_data=message)

    async def kill_ssh_connection(self):
        self.keep_running = False
        if self.ssh_channel is not None:
            self.ssh_channel.close()
        if self.ssh_client is not None:
            self.ssh_client.close()
        await self.send_text_to_client("\r\nSSH connection terminated by user.\r\n")
        await self.close()
        logger.info(f"SSH connection terminated by user {self.scope['user']}")
