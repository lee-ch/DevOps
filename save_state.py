'''
Saves VirtualBox VM's configuration state to JSON file that can be output
as an artifact in a TeamCity build
'''
from __future__ import print_function, absolute_import
import os
import re
import sys
import logging

try:
	import json
except ImportError as e:
	packages = ['json']
	for package in packages:
		try:
			import pip
			pip.main(['install', package])
		except:
			raise Exception('Failed to install required package {0}'.format(package))

password = re.escape("%password%")
data = {
	'vmname': '%vm_name%',
	'ipaddr': '%ipaddress%',
	'username': '%username%',
	'password': password
}

basedir = os.path.abspath(os.path.dirname(__file__))
vm_config = os.path.join(basedir, 'vm_config.json')
with open(vm_config, 'w') as conf:
	json.dump(data, conf)