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
	hd_size     = "%hd_size%"
    hd_port     = "%hd_port%"
    hd_device   = "%hd_device%"
	hd_location = "%hd_location%"
	hd_format   = "%hd_format%"
    vm_name     = "%vm_name%"

	vm = ManageVM()
	exists = vm.vm_exists(vm_name)
	if exists:
		if not vm.has_hard_drive(vm_name):
			try:
				vm.create_hd(hd_size, hd_location, hd_format)
				subprocess.call(['VBoxManage', 'storagectl', vm_name, '--name', 'IDE', '--add', 'ide'])
				vm.attach_harddrive(vm_name, hd_location, 'IDE', str(hd_port), str(hd_device), 'hdd')
				success_msg = 'Created {size} Hard Drive in {location}'.format(size=hd_size, location=hd_location)
				print(success_msg)
			except Exception as e:
				print('Failed to create Hard Drive')
				print(e)
		else:
			print('Hard drive already exists...')
	else:
		print('Virtual Machine {vm} doesn\'t exist'.format(vm_name))
		print('Skipping...')