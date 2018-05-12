'''
Installs SaltStack on VirtualBox VM
'''
from __future__ import print_function, absolute_import
import os
import sys
import logging
import socket
import pip
import time
try:
	import json
except ImportError as e:
	packages = ['json']
	for package in packages:
		try:
			pip.main(['install', package])
		except Exception:
			raise Exception('Failed to install required package {0}'.format(package))

from vboxmanager.utils.sshutil import OpenSSH
from utils.salt.keys import SaltMasterKey


salt_master = "%salt_master%"
hostname = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.hostname%"
ipaddr = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.ipaddress%"
username = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.username%"
password = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.password%"

salt_dir = '/etc/salt'
basedir = os.path.abspath(os.path.dirname(__file__))
vm_config = os.path.join(basedir, 'vm_config.json')
with open(vm_config, 'r') as f:
	data = json.load(f)

def run_command(command):
	if has_ssh_connection(ipaddr):
		ssh = OpenSSH(hostname=ipaddr, username=username, password=password)
		try:
			socket.setdefaulttimeout(timeout)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
			ssh.send_command(command)
		except:
			print('Failed to execute command: ' + command)


if __name__ == '__main__':
	# Install curl, cd into source dir, curl salt bootstrap script and install
	# Salt minion with Master node specified in build parameter
	salt_master = SaltMasterKey('public')
	master_key = salt_master.get_key()
	commands = [
		'sudo apt-get install curl -y',
		'cd /usr/local/src',
		'sudo curl -L https://bootstrap.saltstack.com -o install_salt.sh',
		'sudo sh install_salt.sh -A {}'.format(salt_master),
		'sudo sed -Ei \'s/#master\: salt/master\: {}/\' /etc/salt/minion'.format(salt_master),
		'sudo sed -Ei "s/^#master_finger: .*/master_finger: \'{pub_key}\'/" /etc/salt/minion'.format(pub_key=master_key),
		'sudo echo {} > {}/minion_id'.format(hostname, salt_dir),
		'sudo /etc/init.d/salt-minion restart',
	]

	timeout = 480
	command_wait = 10

	time.sleep(timeout)
	for command in commands:
		run_command(command)
		time.sleep(command_wait)