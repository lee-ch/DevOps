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
	vm_path           = "%vm_path%"
	vm_name           = "%vm_name%"
	os_type           = "%os_type%"
	proc_count        = "%proc_count%"
	cpu_arch          = "%cpu_arch%"
	ram_amount        = "%ram_ammount%"
	network_interface = "%network_interface%"

	if '64' in cpu_arch:
		if '64' not in os_type:
			os_type += '_64'

	vm_exists = False
	for _, subdirs, files in os.walk(vm_path):
		if vm_name in subdirs:
			vm_exists = True

	if not vm_exists:
		vm = ManageVM()
		vm.createVm(vm_name, os_type, proc_count)
		vm.add_ram(vm_name, ram_amount)
		vm.bridged_nic(vm_name, network_interface)
	else:
		print('Virtual Machine {vm} exists'.format(vm=vm_name))
		sys.exit(0)