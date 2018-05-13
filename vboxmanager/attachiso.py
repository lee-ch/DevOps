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
	vm_name      = "%vm_name%"
	storage_ctrl = "%storage_ctrl%"
	device       = "%device%"
	iso_type     = "%iso_type%"
	iso_location = "%iso_location%"

	vm = ManageVM()
	exists = vm.vm_exists(vm_name)
	if exists:
		if not vm.has_dvd_drive(vm_name):
			vm = ManageVM()
			p = subprocess.Popen(
				['VBoxManage', 'showvminfo', vm_name],
				stdout=subprocess.PIPE
			)

			# Get the new port by adding 1 to it
			vminfo = p.communicate()[0]
			matches = re.findall('IDE \((0)\,\s0\)', vminfo)
			cur_port = int(matches[0])
			port = int(matches[0]) + 1

			if port == cur_port:
				# If current port is equal to current port, loop through until it's incremented by 1
				while port == cur_port:
					port += 1
					if port != cur_port:
						break
					else:
						next

			port = str(port)

			try:
				vm.attach_harddrive(vm_name, iso_location, 'IDE', port, device, 'dvddrive')
				success_msg = 'Successfully attached ISO image {location}'.format(location=iso_location)
				print(success_msg)
			except Exception as e:
				print('Failed to attach ISO image {location}'.format(location=iso_location))
				print(e)
		else:
			print('IDE exists, skipping...')
	else:
		print('Virtual Machine {vm} does\'t exist'.format(vm=vm_name))