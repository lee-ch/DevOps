import os
import sys
import subprocess
import logging


def extract_file(file, dest_path):
	if file.endswith('.zip'):
		import zipfile
		zip_ref =  zipfile.ZipFile(file, 'r')
		zip_ref.extractall(dest_path)
		zip_ref.close()
	elif ZipFile.endswith('.tar.gz'):
		import tarfile
		tar = tarfile.open(file, 'r:gz')
		tar.extractall(dest_path)
		tar.close()


if __name__ == '__main__':
	extract_file("%hdzip%", "%zipdestination%")