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
	vm_path           = "%vm_path%"
	vm_name           = "%vm_name%"
	os_type           = "%os_type%"
	proc_count        = "%proc_count%"
	ram_amount        = "%ram_ammount%"
	network_interface = "%network_interface%"

	vm_exists = False
	for _, subdirs, files in os.walk(vm_path):
		if vm_name in subdirs:
			vm_exists = True

	if not vm_exists:
		vm = ManageVM()
		vm.createVm(vm_name, os_type, proc_count)
		vm.add_ram(vm_name, ram_ammount)
		vm.bridged_nic(vm_name, network_interface)
	else:
		print('Virtual Machine {vm} exists'.format(vm=vm_name))
		sys.exit(0)