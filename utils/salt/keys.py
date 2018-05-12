'''
Gets the public or private Salt Master key
'''
import os
import sys
import re
import logging
import time
import datetime

from salt.key import KeyCLI
from salt.cli.key import SaltKey
from salt.utils.parsers import SaltKeyOptionParser


class SaltMasterKey:
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