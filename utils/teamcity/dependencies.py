# Install dependencies for Windows Remote Session
import pip
import sys
import os


def install(package):
	pip.main(['install', package])


if __name__ == '__main__':
	packages = [ 'winrm' ]
	for package in packages:
		install(str(package))