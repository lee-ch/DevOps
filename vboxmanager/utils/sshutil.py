# Utility for sshing into VirtualBox VMs
import sys
import time
import paramiko
import logging
import socket
import time


class OpenSSH:
	def __init__(self, host, port, username, password):
		self.host = host
		self.port = port
		self.username = username
		self.password = password

	def wait_for_ssh(self, timeout, retry_interval):
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		retry_interval = float(retry_interval)
		timeout = int(timeout)
		timeout_start = time.time()
		while time.time() < timeout_start + timeout:
			time.sleep(retry_interval)
			try:
				self.ssh.connect(self.host, int(self.port), self.username, self.password, look_for_keys=False)
			except paramiko.ssh_exception.SSHException as e:
				if e.message == 'Error reading SSH protocol banner':
					print(e)
					continue
				break
			except paramiko.ssh_exception.NoValidConnectionsError as e:
				print('SSH transport is unavailable')

	def send_command(self, command, timeout=900, retry_interval=10):
		'''
		Sends command if connection was made successfully
		'''
		self.wait_for_ssh(timeout, retry_interval)
		stdin, stdout, stderr = self.ssh.exec_command(command)
		while not stdout.channel.exit_status_ready():
			if stdout.channel.recv_ready():
				data = stdout.channel.recv(1024)
				_prev_data = b'1'
				while _prev_data:
					_prev_data = stdout.channel.recv(1024)
					data += _prev_data

				print(str(data))