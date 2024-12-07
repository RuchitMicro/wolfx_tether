# web/consumer.py
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
    SSHConsumer is responsible for handling a WebSocket that proxies
    a remote SSH session. This allows a browser terminal (xterm.js) to
    interactively communicate with a remote host over SSH.

    This consumer:
    - On connect: retrieves the Host data, sets up SSH connection, and opens a shell.
    - On receive: sends incoming data from client to the SSH shell input or handles control commands.
    - On disconnect: closes the SSH connection.

    Run paramiko in a separate thread to avoid blocking the event loop.

    Always handle exceptions gracefully and send an appropriate message
    back to the user if something fails.
    """

    # Store references to SSH session components
    ssh_client = None
    ssh_channel = None
    output_thread = None
    keep_running = True

    async def connect(self):
        # Extract host_id from self.scope['url_route']['kwargs']
        host_id = self.scope['url_route']['kwargs'].get('host_id')
        if not host_id:
            await self.close()
            return

        # Accept WebSocket connection
        await self.accept()

        # Get Host object
        host = None
        try:
            host = await self.get_host(host_id)
        except Exception as e:
            # If we can't get the host, close connection and send error
            await self.send_text_to_client("Error: Unable to fetch host.")
            await self.close()
            return

        # Attempt SSH connection
        try:
            # Paramiko SSH setup
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using password or pem file depending on availability
            if host.pem_file:
                # Use key-based authentication
                pkey = paramiko.RSAKey.from_private_key_file(host.pem_file.path)
                self.ssh_client.connect(
                    hostname=host.ip,
                    port=host.port,
                    username=host.username,
                    pkey=pkey,
                    timeout=10
                )
            else:
                # Use password-based authentication
                self.ssh_client.connect(
                    hostname=host.ip,
                    port=host.port,
                    username=host.username,
                    password=host.password,
                    timeout=10
                )

            # Open an interactive shell
            self.ssh_channel = self.ssh_client.invoke_shell(term='xterm')
            self.ssh_channel.settimeout(0.0)

            # Launch a separate thread to read output from the SSH session
            self.keep_running = True
            self.output_thread = threading.Thread(target=self.read_ssh_output, daemon=True)
            self.output_thread.start()

            logger.info(f"SSH connection established to {host.ip} by user {self.scope['user']}")

        except Exception as e:
            await self.send_text_to_client(f"Error: Unable to establish SSH connection. {str(e)}")
            logger.error(f"SSH connection failed for host_id {host_id}: {str(e)}")
            await self.close()
            return

    async def disconnect(self, close_code):
        # Close SSH connection and channel on disconnect
        self.keep_running = False
        if self.ssh_channel is not None:
            self.ssh_channel.close()
        if self.ssh_client is not None:
            self.ssh_client.close()
        logger.info(f"SSH connection closed for user {self.scope['user']} with close_code {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handle incoming WebSocket messages. Expect JSON messages to distinguish
        between regular input and control commands like 'kill'.
        """
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
                    # Handle kill command
                    await self.kill_ssh_connection()
                else:
                    await self.send_text_to_client("Error: Unknown message type.")
            except json.JSONDecodeError:
                # If message is not JSON, treat it as raw input
                if self.ssh_channel is not None:
                    try:
                        self.ssh_channel.send(text_data)
                    except Exception as e:
                        await self.send_text_to_client(f"\r\nError writing to SSH channel: {str(e)}\r\n")

    def read_ssh_output(self):
        """
        This runs in a separate thread. We continually read from the SSH channel
        and send data back over the WebSocket. Since we cannot use async here,
        we use async_to_sync for sending data to the client.

        We read small chunks of data and send them back to the client as soon as they arrive.
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
        """
        Fetch the Host object asynchronously. Adjust if you're using an async ORM or not.
        If using Django’s default ORM (synchronous), run in thread executor or just get it.
        """
        # Using standard Django ORM call (synchronous)
        # If you're using async consumers, either run_in_executor or 
        # accept that this is a blocking call. For simplicity, we just do it directly.
        # In a real production system, do it with sync_to_async:
        from asgiref.sync import sync_to_async
        return await sync_to_async(get_object_or_404)(Host, id=host_id)

    async def send_text_to_client(self, message):
        """Send a text message to the connected WebSocket client."""
        await self.send(text_data=message)

    async def kill_ssh_connection(self):
        """
        Handle the kill command by closing the SSH connection and the WebSocket.
        """
        self.keep_running = False
        if self.ssh_channel is not None:
            self.ssh_channel.close()
        if self.ssh_client is not None:
            self.ssh_client.close()
        await self.send_text_to_client("\r\nSSH connection terminated by user.\r\n")
        await self.close()
        logger.info(f"SSH connection to host_id {self.scope['url_route']['kwargs'].get('host_id')} terminated by user {self.scope['user']}")
