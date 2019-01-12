# Win32/Grenam remover

Easily remove and revert damage caused by the Win32/Grenam malware.

## huh?

Win32/Grenam, informally referred to as the V-Virus, is known for recursively enumerating through owned .exe files. It replaces executables with itself and thus makes  them inoperable. The threat is most effective in the context of a shared folder, where users mindlessly click on and run executables without checking attributes. Infection looks a little something like:

* user runs infected executable, game.exe
* grenam is executed
* Mutex is created to prevent multiple instances/operations from running at one time.
* game.exe recursively enumerates through writeable, uninfected executables starting at the root of C:. This means anything accessible, including attached volumes.
* Once a file is found, the virus renames a working copy to v<filename>.exe, setting the windows FILE_ATTRIBUTE_SYSTEM and FILE_ATTRIBUTE_READONLY attributes to circumvent detection. To make it less obvious, the original program's icon is included if existent. In the case that none is found, a blank icon v<filename>.ico is created.
* According to a page on MSDN, the virus only runs the original exe after infecting 123 files. This won't take very long.

## Why?

Although a run through virus total yielded quite a promising detection rating, 57 / 69, most anti-virus programs simply delete infected files without proper cleanup. This leaves the users system still worse for wear. For example, desktop and start menu shortcuts remain inoperable. Grenam remover tries it's best to not only eliminate the threat but repair it's effects. The program does it's absolute best to eliminate false positives by only deleting files that correspond to the v<filename> pattern and have an approximate file size. I've yet to see false positives, even across multiple machines.

## Usage

### Binaries

Grenam only searches for *.exe, leaving out other executable formats such as .com. A fully-working com binary can be found on [the releases page](http://github.com/cartertemm/grenam-remover/releases). It might be nice to include this in infected shares if the virus seems to be spreading. However, it is made available only for those users who don't have python or the time/knowledge to compile. When in doubt, build your own.

### Executing

Open a command window in the directory where this program resides.

```
usage: remover.py [-h] [--dry] [-f FILE] [-p PATH]

easily remove the Win32/Grenam.A malware

optional arguments:
  -h, --help            show this help message and exit
  --dry                 Dry run. Only display output, no deletion
  -f FILE, --file FILE  filename to which a list of removed files will be
                        written. If this option is omitted, they will be
                        printed
  -p PATH, --path PATH  path to scan, default is c:\
```

Again, I've yet to see any false positives, and the case of one occurring seems quite rare. But it might be a good idea to first run with the --dry option if only to know what all is about to be sent into the void.

## building

**important!** Only run on machines you know for an absolute fact are 100% clean! The last thing the world needs is another virus remover with a virus, eh? If your not completely sure, grab a binary. Instructions are listed above.
In order to build, you must have a copy of the latest version of python. At the time of this writing that would be [python 3.7](https://www.python.org/downloads/release/python-371), although the thing will probably run on any version of py3 or later.
You'll also have to grab [pyinstaller](http://pyinstaller.org)

Now from commandline, simply run:

```
pyinstaller --onefile remover.py
```

Assuming no errors occurred, remover.exe should now be located in the dist directory. to make sure it's unable to be touched by our old friend, change the extension of .exe to .com.

## Contributing/issues

Have a feature suggestion? Spot a bug? Use the [repositories issue tracker](http://github.com/cartertemm/grenam-remover/issues)
If you'd rather not deal with github, get in contact and I'll see what I can do to help.

## Contact

twitter (probably most efficient): cartertemm
email: crtbraille@gmail.com
