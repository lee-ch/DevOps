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
import datetime
import platform

from pprint import pprint
from vbutils import human_readable_to_bytes

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


def split_no_quotes(string):
	return shlex.split(string)


class VMManager:
	def __init__(self):
		oVBoxMgr = VirtualBoxManager(None, None)
		self.ctx = {
			'global':		oVBoxMgr,
			'vb':			oVBoxMgr.getVirtualBox(),
			'const':		oVBoxMgr.constants,
			'remote':		oVBoxMgr.remote,
			'type':			oVBoxMgr.type,
		}

		self.session = virtualbox.Session()

	def enumFromString(self, enum, str):
		enum = self.ctx['const'].all_values(enum)
		return enum.get(str, None)

	def getState(self, var):
		return 'on' if var else 'off'

	def vmById(self, uuid):
		mach = self.ctx['vb'].findMachine(uuid)
		return mach

	def getMachines(self):
		return self.ctx['global'].getArray(self.ctx['vb'], 'machines')

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
		# update cache
		return self.ctx['global'].getArray(self.ctx['vb'], 'machines')

	def getSession(self, mach):
		session = self.ctx['global'].openMachineSession(mach, fPermitSharing=True)
		return session

	def closeSession(self, mach, cmd, args=[], save=True):
		session = self.ctx['global'].openMachineSession(mach, fPermitSharing=True)
		mach = session.machine
		try:
			cmd(mach, args)
		except Exception as e:
			save = False
		if save:
			try:
				mach.saveSettings()
			except Exception as e:
				print(e)
				traceback.print_exc()
		self.ctx['global'].closeMachineSession(session)

	def detachVm(self, mach, args):
		atts = self.ctx['global'].getArray(mach, 'mediumAttachments')
		hid = args[0]
		for a in atts:
			if a.medium:
				if hid == 'ALL' or a.medium.id == hid:
					mach.detachDevice(a.controller, a.port, a.device)

	def removeVm(self, name):
		mach = self.vmById(name)
		uuid = mach.id
		self.closeSession(mach, self.detachVm, ['ALL'])
		disks = mach.unregister(self.ctx['global'].constants.CleanupMode_Full)
		if mach:
			progress = mach.deleteConfig(disks)
		self.getMachines()

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
			'powerdown':	lambda: console.powerDown()
		}

		try:
			ops[cmd]()
		except KeyboardInterrupt:
			self.ctx['interrupt'] = True
		except Exception as e:
			print(e)

		session.unlockMachine()

	def poweron(self, name):
		mach = self.vmById(name)
		if mach == None:
			return 0
		print('Powering on: %s' % name)
		try:
			self.cmdExistingVm(mach, 'poweron', '')
		except:
			print('Failed to power on %s' % name)
		return 0

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

	def startVm(self, name):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject()
		mach = self.vmById(name)
		mach.launchVMProcess(session, '', '')
		try:
			session.unlockMachine()
		except:
			print('Session is not locked')

	def createHdd(self, size, location, fmt='vdi'):
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

	def attachHdd(self, vm, location, controller, port, slot):
		mach = self.vmById(vm)
		if mach is None:
			return False
		vbox = self.ctx['vb']
		try:
			hdd = vbox.openMedium(location,
								  self.ctx['global'].constants.DeviceType_HardDisk,
								  self.ctx['global'].constants.AccessMode_ReadWrite,
								  False)
		except:
			print('No Hard Drive found at %s' % location)
			return False

		self.cmdClosedVm(
			mach, lambda mach, args: mach.attachDevice(controller, port, slot, self.ctx['global'].constants.DeviceType_HardDisk, hdd.id)
		)
		#mach.attachDevice(controller, port, slot, self.ctx['global'].constants.DeviceType_HardDisk, hdd.id)

	def attachController(self, mach, args):
		[name, bus, ctrltype] = args
		ctr = mach.addStorageController(name, bus)
		if ctrltype != None:
			ctr.controllerType = ctrltype

	def attachCtr(self, vm, ctrname, bus, type):
		ctrltype = self.enumFromString('StorageControllerType', type)
		if ctrltype == None:
			print('Controller type %s unknown' %(type))
			return False

		mach = self.vmById(vm)
		if mach is None:
			return False
		bus = self.enumFromString('StorageBus', bus)
		if bus is None:
			print('Bus type %s unknown' %(bus))
			return False

		self.cmdClosedVm(mach, self.attachController, [ctrname, bus, ctrltype])
		return True