# Creates new VM using VirtaulBox Manager Python Module
import os
import sys
import time
import re
import datetime
import logging

import virtualbox.vbmanager


if __name__ == '__main__':
	vm_path				= '%vmpath%'
	vm_name 			= "%vmname%"
	cpu_arch 			= "%cpuarch%"
	os_type 			= "%ostype%"
	proc_count 			= "%numcpus%"
	ram_amount 			= "%memory%"
	network_interface 	= "%netinterface%"
	controller_name		= "%controllername%"
	controller_type		= "%controllertype%"
	controller_bus		= "%controllerbus%"
	hard_drive_location = "%hd_location%"
	hd_port				= "%hdport%"
	hd_device			= "%hddevice%"
	hd_type				= "%hdtype%"

	if '64' in cpu_arch:
		if '64' not in os_type:
			os_type = os_type + '_64'

	vm = virtualbox.vbmanager.ManageVM()
	for _, subdirs, files in os.walk(vm_path):
		if vm_name not in subdirs:
			# Create our VM if it doesn't exist
			vm.createVm(vm_name, os_type, proc_count)
			vm.add_ram(vm_name, ram_amount)
			vm.bridged_nic(vm_name, network_interface)
			vm.attach_controller(vm_name, controller_name, controller_type, controller_bus)
			vm.attach_harddrive(vm_name, hard_drive_location, controller_name, hd_port, hd_device, hd_type)
			vm.start_vm(vm_name)
	else:
		print('Virtual Machine {vm} exists'.format(vm_name))