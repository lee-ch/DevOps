# Utility for sshing into VirtualBox VMs
import sys
import time
import paramiko
import logging
import socket
import time


class OpenSSH:
	def __init__(self, hostname, username, password, timeout=None):
		self.hostname = hostname
		self.username = username
		self.password = password

		print('Establishing SSH connection {0}...'.format(hostname))
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(self.hostname, username=self.username, password=self.password, look_for_keys=False, timeout=timeout)

	def has_ssh_connection(self, host, port=22, timeout=600):
		'''
		Checks if an SSH connection can be established
		'''
		try:
			socket.setdefaulttimeout(timeout)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
			has_connection = True
		except:
			has_connection = False
		return has_connection

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