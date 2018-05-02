# Utilities for VirtualBox Manager
from __future__ import print_function, absolute_import
import os
import sys
import re
import time
import datetime
import math


SIZE = {
	'G': 1073741824,
	'M': 1048576,
	'K': 1024
}

def human_readable_to_bytes(size, bytes_only=True):
	if size[-1] == 'B':
		size = size[:-1]
	if size.isdigit():
		bytes = int(size)
	else:
		bytes = size[:-1]
		unit = size[-1].upper()
		if bytes.isdigit():
			bytes = int(bytes)
			if unit == 'G':
				bytes *= 1024 ** 3
			elif unit == 'M':
				bytes *= 1024 ** 2
			elif unit == 'K':
				bytes *= 1024
			else:
				bytes = 0
		else:
			bytes = 0
	if bytes_only:
		return bytes
	else:
		return bytes, size+'B'

def human_readable_to_megabyte(size, bytes_only=True):
	if size[-1] == 'B':
		size = size[:-1]
	if size.isdigit():
		bytes = int(size)
	else:
		bytes = size[:-1]
		unit = size[-1].upper()
		if bytes.isdigit():
			bytes = int(bytes)
			if unit == 'M':
				bytes *= 1024
			else:
				bytes = 0
		else:
			bytes = 0
	if bytes_only:
		return bytes