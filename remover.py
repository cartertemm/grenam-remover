#Copyright (c) 2019 Carter Temm
#this file is covered by the MIT license
#see license for more info

#sizes of grenam binaries, paint.exe
#A couple strains seem to be lurking around, just add to the list
#change this as needed
#enable system and hidden files, then browse to %appdata%\paint.exe. Click properties, use object nav to find size, and enter it here

EXE_SIZES=[844288, 849920]

import os
import fnmatch
import sys
import subprocess
import argparse

#grenam sets FILE_ATTRIBUTE_SYSTEM and FILE_ATTRIBUTE_READONLY to circumvent detection and deletion
#we need GetFileAttributes and SetFileAttributes from the winapi to reverse this
import ctypes


def is_admin():
	"""checks to see if the program is being run as an administrator"""
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return 0

def cmd(command):
	"""runs a command and returns stdout and stderr"""
	output=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	result=(output.stdout.read()+output.stderr.read()).strip()
	return result

def scan():
	"""performs a scan of the filesystem to find infected files"""
	global num
	num=0
	matches=[]
	for root, dirnames, filenames in os.walk(args.path):
		for filename in fnmatch.filter(filenames, "v*.exe"):
			good_file=os.path.join(root, filename)
			bad_file=os.path.join(root, filename[1:])
			if os.path.isfile(bad_file):
				if is_grenam_size(bad_file):
					num+=1
					matches.append(bad_file)
					if not args.dry:
						#change file attributes to match the original
						attribs=ctypes.windll.kernel32.GetFileAttributesW(bad_file)
						os.remove(bad_file)
						os.rename(good_file, bad_file)
						ctypes.windll.kernel32.SetFileAttributesW(bad_file, attribs)
					ico=os.path.join(root, filename[:-3]+"ico")
					if os.path.isfile(ico):
						matches.append(ico)
						if not args.dry:
							os.remove(ico)
	return matches

def is_grenam_size(filename):
	"""checks to see if an executable is grenam by size alone"""
	size=int(os.stat(filename).st_size)
	if size in EXE_SIZES:
		return True
	return False

num=0
parser=argparse.ArgumentParser(description="easily remove the Win32/Grenam.A malware")
parser.add_argument("--dry", action="store_true", help="Dry run. Only display output, no deletion")
parser.add_argument("-f", "--file", help="filename to which a list of removed files will be written. If this option is omited, they will be printed")
parser.add_argument("-p", "--path", help="path to scan, default is c:\\", default="c:\\")
args=parser.parse_args()

print("grenam removal tool v 1.0")
print("Written by Carter Temm <http://github.com/cartertemm/grenam-remover>")
if not is_admin():
	print("Warning! For optimal performence and quality, make sure to run this program as admin")
print("scanning for virus...")
if not os.path.exists(args.path):
	print("error, non-existent path provided")
	sys.exit()
path=os.path.join(os.environ["appdata"], "paint.exe")
if os.path.isfile(path):
	print("found paint.exe in appdata")
	if is_grenam_size(path):
		print("system appears to be infected")
		if not args.dry:
			print("removing")
			#we now pray to god above that taskkill didn't become infected somehow
			cmd("taskkill /f /im paint.exe")
			os.remove(path)
else:
	print("not found in appdata")
startup_location=os.path.join(os.environ["appdata"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "paint.lnk")
if os.path.isfile(startup_location):
	print("found in startup")
	if not args.dry:
		print("removing")
		os.remove(startup_location)
else:
	print("not found in startup")
print("scanning for "+("and removing " if not args.dry else "")+" infected files. This might take a while")
s=scan()
print("a total of "+str(num)+" files were found "+("and cleaned up" if not args.dry else ""))
if args.file:
	f=open(args.file, "w")
	f.write("\n".join(s))
	f.close()
else:
	print("\n".join(s))