'''
Installs SaltStack on VirtualBox VM
'''
from __future__ import print_function, absolute_import
import os
import sys
import logging
import pip
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


basedir = os.path.abspath(os.path.dirname(__file__))
vm_config = os.path.join(basedir, 'vm_config.json')
with open(vm_config, 'r') as f:
	data = json.load(f)

ipaddr = data['ipaddr']
username = data['username']
password = data['password']

def run_command(command):
	ssh = OpenSSH(hostname=ipaddr,
				  username=username,
				  password=password,
				  command=command)

	ssh.send_command(command)