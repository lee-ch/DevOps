import os
import sys
import re
import logging

from vboxmanager.vbmanager import ManageVM


if __name__ == '__main__':
	vm_name = "%vm_name%"

	vm = ManageVM()
	if not vm.is_running(vm_name) and vm.is_running(vm_name) is not None:
		print('Starting VM: ' + vm_name)
		try:
			vm.startVm(vm_name)
			print('Started VM: ' + vm_name)
		except:
			print('Failed to start VM: ' + vm_name)