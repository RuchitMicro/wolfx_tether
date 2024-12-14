# consumers.py
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
    """
    Opinionated approach:
    This consumer no longer enforces a permission check for the host. 
    Instead, it only checks if the user is authenticated.
    If authenticated, it proceeds to connect to the host. 
    If not authenticated, it sends an error to the client and closes the connection.

    If the host does not exist or SSH fails, it gracefully notifies the client.
    """

    ssh_client = None
    ssh_channel = None
    output_thread = None
    keep_running = True

    async def connect(self):
        # Extract host_id from URL kwargs
        host_id = self.scope['url_route']['kwargs'].get('host_id')
        if not host_id:
            # No host_id means we cannot proceed
            await self.accept()
            await self.send_text_to_client("Error: No host ID specified.")
            await self.close()
            return

        # Check if user is authenticated
        if not self.scope['user'].is_authenticated:
            # Inform the user and close
            await self.accept()
            await self.send_text_to_client("Error: You must be authenticated to access this host.")
            await self.close()
            return

        # Accept the connection now that authentication passed
        await self.accept()

        # Fetch the host object
        try:
            host = await self.get_host(host_id)
        except Exception as e:
            await self.send_text_to_client("Error: Unable to fetch host details.")
            await self.close()
            return

        # Attempt SSH connection
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if host.use_credential == 'pem':
                # Decrypt the PEM data
                decrypted_pem = host.decrypt_pem(host.encrypted_pem)
                if not decrypted_pem:
                    raise ValueError("Decryption of PEM file failed.")

                # Load the key from decrypted PEM data
                pkey = paramiko.RSAKey.from_private_key(io.StringIO(decrypted_pem.decode('utf-8')))
                self.ssh_client.connect(
                    hostname=host.host_address,
                    port=host.port,
                    username=host.username,
                    pkey=pkey,
                    timeout=10
                )
            elif host.use_credential == 'password':
                decrypted_password = host.decrypt_password(host.password)
                self.ssh_client.connect(
                    hostname=host.host_address,
                    port=host.port,
                    username=host.username,
                    password=decrypted_password,
                    timeout=10
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
            await self.send_text_to_client(f"Error: Unable to establish SSH connection. {str(e)}")
            logger.error(f"SSH connection failed for host_id {host_id}: {str(e)}")
            await self.close()

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
        """
        Runs in a separate thread. Continuously reads from SSH channel and
        sends the output to the client in near real-time.
        """
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
        """
        Send plain text messages back to the WebSocket client.
        """
        await self.send(text_data=message)

    async def kill_ssh_connection(self):
        """
        Close the SSH connection and notify the client that the session ended.
        """
        self.keep_running = False
        if self.ssh_channel is not None:
            self.ssh_channel.close()
        if self.ssh_client is not None:
            self.ssh_client.close()
        await self.send_text_to_client("\r\nSSH connection terminated by user.\r\n")
        await self.close()
        logger.info(f"SSH connection terminated by user {self.scope['user']}")
