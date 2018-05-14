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



def run_command(command, host, port, timeout, interval):
	ssh = OpenSSH(host=ipaddr, port=port, username=username, password=password)
	ssh.send_command(command, timeout, interval)

if __name__ == '__main__':
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

	# Install curl, cd into source dir, curl salt bootstrap script and install
	# Salt minion with Master node specified in build parameter
	salt_master = SaltMasterKey('public')
	master_key = salt_master.get_key()
	commands = [
		r'sudo apt-get install curl -y',
		r'sudo curl -L https://bootstrap.saltstack.com -o install_salt.sh',
		r'sudo sh install_salt.sh -A {}'.format(salt_master_ip),
		r'sudo sed -Ei "s/^#master\: salt/master\: {}/" /etc/salt/minion'.format(salt_master_ip),
		r'sudo sed -Ei "s/^#master_finger: .*/master_finger: \'{pub_key}\'/" /etc/salt/minion'.format(pub_key=master_key),
		r'sudo rm -f /etc/salt/minion_id',
		r'sudo sed -i "s/^#grains\:/grains\:\n  uuid\: \'{uuid}\'/" /etc/salt/minion'.format(uuid=MINION_UUID),
		r'sudo sed -Ei "s/^#autosign_grains\:/autosign_grains\:/" /etc/salt/minion',
		r'sudo sed -Ei "s/^#(.*\- uuid)/\1/" /etc/salt/minion',
		r'sudo sed -i "s/^#id\:/id\: {}/" /etc/salt/minion'.format(hostname),
		r'sudo /etc/init.d/salt-minion restart'
	]

	for command in commands:
		run_command(command=command, host=ipaddr, port=22, timeout=600, interval=1)
		time.sleep(10)