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
import uuid

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


# Creates the UUID to be used to accept the Minions key on the Master
NAMESPACE_STR = 'linuxminion'
MINION_UUID = str(uuid.uuid3(uuid.NAMESPACE_DNS, NAMESPACE_STR))

salt_dir = '/etc/salt'
minion_file = os.path.join(salt_dir, 'minion_id')
basedir = os.path.abspath(os.path.dirname(__file__))
salt_master_ip = "%salt_master%"
hostname = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.hostname%"
ipaddr = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.ipaddress%"
username = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.username%"
password = "%reverse.dep.VirtualBox_BuildVirtualMachine_LinuxMinion.password%"

def run_command(command, host, port, timeout):
	ssh = OpenSSH(hostname=ipaddr, username=username, password=password, timeout=timeout)
	try:
		ssh.send_command(command)
	except:
		print('Failed to execute command: ' + command)


if __name__ == '__main__':
	# We need to wait until the VM is up and running
	# (will automate this process at some point but for now, this works)
	timeout = 900

	# Install curl, cd into source dir, curl salt bootstrap script and install
	# Salt minion with Master node specified in build parameter
	salt_master = SaltMasterKey('public')
	master_key = salt_master.get_key()
	commands = [
		'sudo apt-get install curl -y',
		'cd /usr/local/src',
		'sudo curl -L https://bootstrap.saltstack.com -o install_salt.sh',
		'sudo sh install_salt.sh -A {}'.format(salt_master_ip),
		'sudo sed -Ei \'s/#master\: salt/master\: {}/\' /etc/salt/minion'.format(salt_master_ip),
		'sudo sed -Ei "s/^#master_finger: .*/master_finger: \'{pub_key}\'/" /etc/salt/minion'.format(pub_key=master_key),
		'sudo echo {} > {}'.format(hostname, minion_file),
		'sudo /etc/init.d/salt-minion restart',
		'sudo sed -Ei "s/^#.*(\- uuid)/\1\n  {uuid}/"'.format(MINION_UUID)
	]

	for command in commands:
		run_command(command, ipaddr, 22, timeout)
		time.sleep(10)