'''
Creates new base VM
'''
import os
import time
import sys
import re
import logging
import time
import datetime
import subprocess

from vboxmanager.vbmanager import ManageVM


if __name__ == '__main__':
	vm_name     = "%vm_name%"
	hd_size     = "%hd_size%"
	hd_port     = "%hd_port%"
	hd_format   = "%hd_format%"
	hd_device   = "%hd_device%"
	hd_location = "%hd_location%"

	try:
		vm = ManageVM()
		vm.create_hd(hd_size, hd_location, hd_format)
		subprocess.call(['VBoxManage', 'storagectl', vm_name, '--name', 'IDE', '--add', 'ide'])
		vm.attach_harddrive(vm_name, hd_location, 'IDE', str(hd_port), str(hd_device), 'hdd')
		success_msg = 'Created {size} Hard Drive in {location}'.format(size=hd_size, location=hd_location)
		print(success_msg)
	except Exception as e:
		print('Failed to create Hard Drive')
		print(e)