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
	vm_name           = "%vm_name%"
	os_type           = "%os_type%"
	proc_count        = "%proc_count%"
	cpu_arch          = "%cpu_arch%"
	ram_amount        = "%ram_ammount%"
	network_interface = "%network_interface%"

	if '64' in cpu_arch:
		if '64' not in os_type:
			os_type += '_64'

	vm = ManageVM()
	exists = vm.vm_exists(vm_name)
	if not exists:
		vm.createVm(vm_name, os_type, proc_count)
		vm.add_ram(vm_name, ram_amount)
		vm.bridged_nic(vm_name, network_interface)
	else:
		print('Virtual Machine {vm} exists'.format(vm=vm_name))
		print('Skipping...')