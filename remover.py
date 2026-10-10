# Copyright (c) 2019 Carter Temm (Modified for dynamic detection, recursive scanning & robust attribute handling)
# This file is covered by the MIT license

EXE_SIZES = [844288, 849920]
FILE_ATTRIBUTE_NORMAL = 128  # Reset file attributes to normal (0x80)

import os
import sys
import subprocess
import argparse
import ctypes

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return 0

def clear_attributes(filepath):
    """Removes Read-Only, System, and Hidden flags so files can be modified or deleted."""
    try:
        ctypes.windll.kernel32.SetFileAttributesW(filepath, FILE_ATTRIBUTE_NORMAL)
    except Exception:
        pass

def cmd(command):
    """Runs a shell command and returns output."""
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = (output.stdout.read() + output.stderr.read()).strip()
    return result

def is_grenam_size(filename):
    """Checks if an executable matches known Grenam virus file sizes."""
    try:
        size = int(os.stat(filename).st_size)
        return size in EXE_SIZES
    except Exception:
        return False

def walk_error_handler(error):
    """Silently skips folders with permission restrictions during recursive search."""
    pass

def scan():
    """Performs a recursive scan of all folders and subfolders to find and fix infected files."""
    global num
    num = 0
    matches = []
    
    for root, dirnames, filenames in os.walk(args.path, onerror=walk_error_handler):
        for filename in filenames:
            if filename.lower().startswith("v") and filename.lower().endswith(".exe"):
                good_file = os.path.join(root, filename)
                bad_file = os.path.join(root, filename[1:])  # Strip leading 'v'
                
                if os.path.isfile(bad_file):
                    if is_grenam_size(bad_file):
                        num += 1
                        matches.append(bad_file)
                        
                        if not args.dry:
                            try:
                                # 1. Clear Read-Only/System attributes from virus file before deletion
                                clear_attributes(bad_file)
                                os.remove(bad_file)
                                
                                # 2. Clear Hidden attributes from clean original file before renaming
                                clear_attributes(good_file)
                                os.rename(good_file, bad_file)
                                
                                # 3. Ensure restored file has clean Normal attributes
                                clear_attributes(bad_file)
                            except Exception as e:
                                print(f"Error repairing {bad_file}: {e}")
                        
                        ico = os.path.join(root, filename[:-3] + "ico")
                        if os.path.isfile(ico):
                            matches.append(ico)
                            if not args.dry:
                                try:
                                    clear_attributes(ico)
                                    os.remove(ico)
                                except Exception:
                                    pass
    return matches

num = 0
parser = argparse.ArgumentParser(description="Easily remove the Win32/Grenam.A malware across all subfolders")
parser.add_argument("--dry", action="store_true", help="Dry run. Only display output, no deletion")
parser.add_argument("-f", "--file", help="Filename to write clean results log to")
parser.add_argument("-p", "--path", help="Path to scan, default is C:\\", default="C:\\")
args = parser.parse_args()

print("Grenam removal tool v1.2 (Dynamic Detection & Recursive Edition)")
print("Written by Carter Temm <http://github.com/cartertemm/grenam-remover>")
if not is_admin():
    print("Warning! For optimal performance and quality, make sure to run this program as admin")

if not os.path.exists(args.path):
    print("Error: non-existent path provided")
    sys.exit()

print("Scanning for active virus processes in appdata & startup...")
appdata_path = os.environ.get("appdata", "")
paint_path = os.path.join(appdata_path, "paint.exe") if appdata_path else ""

if paint_path and os.path.isfile(paint_path):
    print("Found paint.exe in appdata")
    try:
        detected_size = os.path.getsize(paint_path)
        if detected_size not in EXE_SIZES:
            EXE_SIZES.append(detected_size)
            print(f"Dynamically added active Grenam signature size: {detected_size} bytes")
    except Exception:
        pass

    if is_grenam_size(paint_path):
        print("System appears to be infected")
        if not args.dry:
            print("Removing paint.exe process and binary...")
            cmd("taskkill /f /im paint.exe")
            clear_attributes(paint_path)
            try:
                os.remove(paint_path)
            except Exception:
                pass
else:
    print("Not found in appdata")

startup_location = os.path.join(appdata_path, "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "paint.lnk")
if os.path.isfile(startup_location):
    print("Found paint shortcut in startup")
    if not args.dry:
        print("Removing startup shortcut...")
        clear_attributes(startup_location)
        try:
            os.remove(startup_location)
        except Exception:
            pass
else:
    print("Not found in startup")

print("Scanning for " + ("and removing " if not args.dry else "") + "infected files across all subfolders. This might take a while...")
s = scan()
print("A total of " + str(num) + " files were found " + ("and cleaned up" if not args.dry else ""))

if args.file:
    try:
        with open(args.file, "w") as f:
            f.write("\n".join(s))
        print(f"Results written to {args.file}")
    except Exception as e:
        print(f"Failed to write log file: {e}")
else:
    if s:
        print("\n".join(s))