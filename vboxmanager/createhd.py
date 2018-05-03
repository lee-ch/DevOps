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
	hd_size     = "%hd_size%"
	hd_location = "%hd_location%"
	hd_format   = "%hd_format%"

	try:
		vm = ManageVM()
		vm.create_hd(hd_size, hd_location, hd_format)
		success_msg = 'Created {size} Hard Drive in {location}'.format(hd_size, hd_location)
		print(success_msg)
	except Exception as e:
		print('Failed to create Hard Drive')
		print(e)