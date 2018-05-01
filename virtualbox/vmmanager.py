# Python modules Virtual Machine Manager
# Manages VMs in VirtualBox through the VirtualBox API and SDK
# ------------------------------------------------------------- #
from __future__ import print_function, absolute_import
import os
import sys
import time
import datetime

try:
	import vboxapi
	import virtualbox
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



class VMManager:
	def __init__(self, name):
		from vboxapi import VirtualBoxManager

		oVBoxMgr = VirtualBoxManager(None, None)
		self.ctx = {
			'global':	oVBoxMgr,
			'vb':		oVBoxMgr.getVirtualBox(),
			'const':	oVBoxMgr.constants,
			'remote':	oVBoxMgr.remote,
			'type':		oVBoxMgr.type,
		}
		self.name = name
		self.session = virtualbox.Session()

	def poweron(self):
		vbox = virtualbox.VirtualBox()
		vm = vbox.find_machine(self.name)
		vm.launch_vm_process(self.session, 'gui')

	def poweroff(self):
		self.session.console.power_down()

	def getVmSession(self, ctx, mach, cmd, args=[], save=True):
		session = ctx['global'].openMachineSession(mach, fPermitSharing=True)
		mach = session.machine
		try:
			cmd(ctx, mach, args)
		except Exception as e:
			save = False
			print(ctx, e)
		if save:
			try:
				mach.saveSettings()
			except Exception as e:
				print(ctx, e)

		self.ctx['global'].closeMachineSession(session)


class CreateNewVM(VMManager):
	def detachVm(self, ctx, mach, args):
		atts = ctx['global'].getArray(mach, 'mediumAttachments')
		hid = args[0]
		for a in atts:
			if a.medium:
				if hid == 'ALL' or a.medium.id == hid:
					mach.detachDevice(a.controller, a.port, a.device)

	def createVm(self, os):
		vbox = self.ctx['vb']
		mach = vbox.createMachine('', self.name, [], os, '')
		mach.saveSettings()
		vbox.registerMachine(mach)
		# Update cache
		#self.getMachines(ctx, True)

	def removeVm(self, ctx, mach):
		uuid = mach.id
		self.getVmSession(self.ctx, mach, self.detachVm, ['ALL'])
		disks = mach.unregister(ctx['global'].constants.CleanupMode_Full)