# Downloads the given Hard Drive
import os
import sys
import subprocess
import logging


def get_hard_drive(url):
	try:
		print('Downloading drive {url}'.format(url=url))
		subprocess.call(['wget', url])
	except Exception as e:
		print('Failed to retrieve drive from {url}'.format(url=url))


if __name__ == '__main__':
	get_hard_drive("%harddrive_url%")