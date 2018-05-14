'''
Gets the public or private Salt Master key
'''
import os
import sys
import re
import logging
import time
import datetime

import salt.config
import salt.wheel

from salt.key import KeyCLI
from salt.cli.key import SaltKey
from salt.utils.parsers import SaltKeyOptionParser


class SaltMasterKey(object):
	def __init__(self, key_name):
		self.key_name = key_name
		
		_key = self.key_name.lower()
		if _key.startswith('priv'):
			self.key_name = 'master.pem'
		elif _key.startswith('pub'):
			self.key_name = 'master.pub'

	def get_key(self):
		parser = SaltKeyOptionParser()
		parser.parse_args()
		config = parser.config

		config['finger_all'] = True
		config['finger'] = self.key_name

		keys = KeyCLI(parser.config)

		# We want to supress stdout so we don't get two keys back from keys.run()
		with open(os.devnull, 'w') as devnull:
			old_stdout = sys.stdout
			sys.stdout = devnull
			key = keys.run()
			sys.stdout = old_stdout

		pub_key = key['local'][self.key_name]
		return pub_key


class UnacceptedKey(SaltMasterKey):
	def __init__(self):
		self.key_name = 'minions_pre'

	def get_unaccepted(self):
		parser = SaltKeyOptionParser()
		parser.parse_args()
		config = parser.config
		config['finger_all'] = True
		keys = KeyCLI(config)

		with open(os.devnull, 'w') as devnull:
			old_stdout = sys.stdout
			sys.stdout = devnull
			key = keys.run()
			sys.stdout = old_stdout

		if key.get(self.key_name, None) is not None:
			unaccepted = key[self.key_name]
			return unaccepted
		return None


class ManageKey(UnacceptedKey):
	def delete_unaccepted(self):
		opts = salt.config.master_config('/etc/salt/master')
		wheel = salt.wheel.WheelClient(opts)

		salt_master = opts['interface']
		keys = super(ManageKey, self).get_unaccepted()
		if keys is not None:
			unaccepted_keys = keys.get_unaccepted()
			for host, key in unaccepted_keys.items():
				wheel.cmd_async({'fun': 'key.delete', 'match': host})
		else:
			print('No unaccepted keys found on Salt Master ' + salt_master)