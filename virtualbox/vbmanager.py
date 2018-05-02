# Python modules Virtual Machine Manager
# Manages VMs in VirtualBox through the VirtualBox API and SDK
# ------------------------------------------------------------- #
from __future__ import print_function, absolute_import
import os
import gc
import sys
import traceback
import shlex
import re
import time
import subprocess
import datetime
import platform

from pprint import pprint
from virtualbox.vbutils import human_readable_to_bytes, human_readable_to_megabyte

try:
	import json
except ImportError:
	import simplejson as json

try:
	import vboxapi
	import virtualbox

	from vboxapi import VirtualBoxManager
except ImportError as e:
	try:
		import pip
		print('Failed to import required modules vboxapi and pyvbox')

		# If pip is installed, use it to install dependencies
		for package in ('vboxapi', 'virtualbox'):
			try:
				print('Attempting to install {0}'.format(package))
				pip.main(['install'], package)
				try:
					__import__('{0}'.format(package))
				except ImportError as e:
					# If we don't have the package by now, raise an import error
					raise Exception('Failed to import module: {0}'.format(e))
			except Exception as er:
				raise Exception('Failed to install package {0}'.format(e))
	except ImportError:
		print('Failed to import Python Package Manager \'pip installer\'')


class ManageVM:
	def __init__(self, vm=''):
		self.vm = vm
		oVBoxMgr = VirtualBoxManager(None, None)
		self.ctx = {
			'global':		oVBoxMgr,
			'vb':			oVBoxMgr.getVirtualBox(),
			'const':		oVBoxMgr.constants,
			'remote':		oVBoxMgr.remote,
			'type':			oVBoxMgr.type,
		}

		self.session = virtualbox.Session()

	def getSession(self, mach):
		session = self.ctx['global'].openMachineSession(mach, fPermitSharing=True)
		return session

	def enumFromString(self, enum, str):
		enum = self.ctx['const'].all_values(enum)
		return enum.get(str, None)

	def getState(self, var):
		return 'on' if var else 'off'

	def vmById(self, uuid):
		vm = self.ctx['vb'].findMachine(uuid)
		return vm

	def getMachines(self):
		if self.ctx['vb'] is not None:
			return self.ctx['global'].getArray(self.ctx['vb'], 'machines')
		else:
			return []

	def argsToVm(self, args):
		uuid = args[1]
		vm = self.vmById(uuid)
		if vm == None:
			print('Unknown VM \'%s\'' % (uuid))
		return vm

	def cmdClosedVm(self, mach, cmd, args=[], save=True):
		session = self.ctx['global'].openMachineSession(mach, fPermitSharing=True)
		mach = session.machine
		try:
			cmd(mach, args)
		except Exception as e:
			save = False
			print(e)
		if save:
			try:
				mach.saveSettings()
			except Exception as e:
				print(e)
				traceback.print_exc()
		self.ctx['global'].closeMachineSession(session)

	def cmdExistingVm(self, mach, cmd, args):
		vbox = self.ctx['vb']
		session = self.ctx['global'].openMachineSession(mach, fPermitSharing=True)
		if session.state != self.ctx['const'].SessionState_Locked:
			print('Session to \'%s\' in wrong state: %s' % (mach.name, session.state))
			session.unlockMachine()
			return
		if self.ctx['remote'] and cmd == 'localhost':
			session.unlockMachine()
			return
		console = session.console
		ops = {
			'pause':		lambda: console.pause(),
			'resume':		lambda: console.resume(),
			'poweron':		lambda: console.powerButton(),
			'powerdown':	lambda: console.powerDown(),
			'powerbutton':	lambda: console.powerButton(),
		}

		try:
			ops[cmd]()
		except KeyboardInterrupt:
			self.ctx['interrupt'] = True
		except Exception as e:
			print(e)

	def createVm(self, name, os):
		# We want to check if the os passed in is an actual os that's supported
		try:
			self.ctx['vb'].getGuestOSType(os)
		except Exception:
			print('Unknown OS type: %s' % os)

		vbox = self.ctx['vb']
		mach = vbox.createMachine('', name, [], os, '')
		mach.saveSettings()
		vbox.registerMachine(mach)
		return self.ctx['global'].getArray(self.ctx['vb'], 'machines')

	def removeVm(self, name):
		mach = self.vmById(name)
		uuid = mach.id
		self.closeSession(mach, self.detachVm, ['ALL'])
		disks = mach.unregister(self.ctx['global'].constants.CleanupMode_Full)
		if mach:
			progress = mach.deleteConfig(disks)
		self.getMachines()

	def get_running_vms(self):
		'''
		Return list of ids of currently running VMs
		'''
		output = subprocess.Popen(
			['VBoxManage', 'list', 'runningvms'],
			stdout=subprocess.PIPE
		).communicate()[0]
		vms = []
		if output is not None:
			lines = output.split('\n')
			for line in lines:
				pattern = re.compile(r'.*{(.*)}')
				match = pattern.match(line)
				if match:
					vms.append(match.group(1))
		return vms

	def create_vm(self, vm_id, os_type, proc_count=2):
		'''
		Simple wrapper around VBoxManage to create a new VM
		'''
		print('Creating VM: {0} -- {1}'.format(vm_id, os_type))
		try:
			subprocess.call(['VBoxManage',
							 'createvm',
							 '--name', vm_id,
							 '--ostype', os_type,
							 '--register'])
			subprocess.call(['VBoxManage', 'modifyvm', vm_id, '--cpus', proc_count])
		except Exception as e:
			print('Failed to create VM: {0} -- {1}: {2}'.format(vm_id, os_type, e))

	def poweroff_vm(self, vm_id):
		'''
		Issues a 'poweroff' command to given VM
		'''
		print('Powering off VM: {0}...'.format(vm_id))
		subprocess.call(['VBoxManage', 'controlvm', vm_id, 'poweroff'])

	def start_vm(self, vm_id):
		'''
		Start the VM passed in by 'vm_id'
		'''
		print('Powering on VM: {0}...'.format(vm_id))
		try:
			subprocess.call(['VBoxManage', 'startvm', vm_id])
			print('VM: {0} started successfully'.format(vm_id))
		except Exception as e:
			print('Failed to start VM: {0} -- {1}'.format(vm_id, e))

	def remove_vm(self, vm_id):
		'''
		Simple wrapper around VBoxManage to remove a VM
		'''
		print('Removing VM: {0}'.format(vm_id))
		try:
			subprocess.call(['VBoxManage',
							  'unregistervm',
							  vm_id,
							  '--delete'])
		except Exception as e:
			print('Failed to remove VM: {0}'.format(vm_id))

	def poweroff(self, name):
		mach = self.vmById(name)
		if mach == None:
			return 0
		print('Powering down: %s' % name)
		try:
			self.cmdExistingVm(mach, 'powerdown', '')
		except:
			print('Failed to power down %s' % name)
		return 0

	def powerbutton(self, args):
		vm = self.argsToVm(args)
		if vm == None:
			return False
		self.cmdExistingVm(vm, 'powerbutton', '')

	def startVm(self, name):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject()
		mach = self.vmById(name)
		mach.launchVMProcess(session, '', '')
		try:
			session.unlockMachine()
		except:
			print('Session is not locked')

	def resumeVm(self, args):
		vm = self.argsToVm(args)
		if vm == None:
			return False
		self.cmdExistingVm(vm, 'resume', '')

	def get_vm_info(self, vm):
		print('Virtual Machine: {0}'.format(vm))
		try:
			subprocess.call(['VBoxManage', 'showvminfo', vm])
		except:
			print('Failed to get info for Virtaul Machine: {0}'.format(vm))

	def add_ram(self, vm, ram):
		mem = human_readable_to_megabyte(str(ram))
		print('Adding {0} of RAM to VM: {1}'.format(ram, vm))
		try:
			p = subprocess.Popen(
				['VBoxManage', 'modifyvm', vm, '--memory', str(mem)],
				stdout=subprocess.PIPE
			)

			p.communicate()[0]
			print('Added {0} of RAM to VM: {1}'.format(ram, vm))
		except Exception as e:
			print('Failed to add {0} of RAM to VM: {1}'.format(ram, vm))
			print(e)

	def bridged_nic(self, vm, interface):
		try:
			subprocess.call(['VBoxManage', 'modifyvm', vm, '--bridgeadapter1', interface])
			try:
				subprocess.call(['VBoxManage', 'modifyvm', vm, '--nic1', 'bridged'])
			except:
				print('Failed to add bridged NIC')
		except:
			print('Failed to add bridged adapter {0}'.format(interface))

	def create_hd(self, size, location, fmt='vdi'):
		'''
		Creates a Hard Drive for vm
		'''
		size = human_readable_to_bytes(size)
		try:
			hdd = self.ctx['vb'].createMedium(fmt,
											  location, 
											  self.ctx['global'].constants.AccessMode_ReadWrite,
											  self.ctx['global'].constants.DeviceType_HardDisk)
			hdd.createBaseStorage(size, (self.ctx['global'].constants.MediumVariant_Standard, ))
		except Exception:
			print('Failed to create Hard Drive %s' % location)

	def attach_controller(self, vm, ctrlname='SATA Controller', type='sata', bus='IntelAhci'):
		success_msg = 'Attached {ctrlr} to {vm}'.format(ctrlr=ctrlname, vm=vm)
		try:
			subprocess.call(
				['VBoxManage',
				 'storagectl', vm,
				 '--name', ctrlname,
				 '--add', type,
				 '--controller', bus]
			)
			print(success_msg)
		except Exception as e:
			print('Failed to controller {ctrlr}'.format(ctrlr=ctrlname))
			print(e)

	def attach_harddrive(self, vm, location, ctrlname, port='0', device='0', type='hdd'):
		success_msg = 'Attached Hard Drive {type} to {vm}'.format(type=type.upper(), vm=vm)
		try:
			subprocess.call(
				['VBoxManage',
				 'storageattach', vm,
				 '--storagectl', ctrlname,
				 '--port', port,
				 '--device', device,
				 '--type', type,
				 '--medium', location]
			)
			print(success_msg)
		except Exception as e:
			print('Failed to attach Hard Drvie {type} to {vm}'.format(type=type.upper(), vm=vm))
