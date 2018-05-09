# Utility for sshing into VirtualBox VMs
import sys
import time
import paramiko
import logging


class OpenSSH:
	def __init__(self, hostname, username, password):
		self.hostname = hostname
		self.username = username
		self.password = password

		print('Establishing SSH connection {0}...'.format(hostname))
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(hostname, username=username, password=password, look_for_keys=False)

	def send_command(self, command):
		'''
		Sends command if connection was made successfully
		'''
		if (self.ssh):
			stdin, stdout, stderr = self.ssh.exec_command(command)
			while not stdout.channel.exit_status_ready():
				if stdout.channel.recv_ready():
					data = stdout.channel.recv(1024)
					_prev_data = b'1'
					while _prev_data:
						_prev_data = stdout.channel.recv(1024)
						data += _prev_data

					print(str(data))