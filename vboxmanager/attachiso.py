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

from vboxmanager.vbmanager import ManageVM


if __name__ == '__main__':
	vm_path      = "%vm_path%"
	vm_name      = "%vm_name%"
	storage_ctrl = "%storage_ctrl%"
	port         = "%port%"
	device       = "%device%"
	iso_type     = "%iso_type%"
	iso_location = "%iso_location%"

	vm_exists = False
	for _, subdirs, files in os.walk(vm_path):
		if vm_name not in subdirs:
			vm_exists = True

	if vm_exists:
		vm = ManageVM()
		try:
			vm.attach_iso(vm_name, storage_ctrl, port, device, iso_type, iso_location)
			success_msg = 'Successfully attached ISO image {location}'.format(location=iso_location)
			print(success_msg)
		except Exception as e:
			print('Failed to attach ISO image {location}'.format(location=iso_location))
			print(e)
	else:
		print('Virtual Machine {vm} does not exist'.format(vm=vm_name))
		sys.exit(0)