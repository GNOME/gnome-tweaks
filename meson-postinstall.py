#!/usr/bin/env python3

import sysconfig
from compileall import compile_dir
from os import environ, path
from subprocess import call

prefix = environ.get('MESON_INSTALL_PREFIX', '/usr/local')
datadir = path.join(prefix, 'share')
destdir = environ.get('DESTDIR', '')

# Package managers set this so we don't need to run
if not destdir:
    print('Updating icon cache...')
    call(['gtk-update-icon-cache', '-qtf', path.join(datadir, 'icons', 'hicolor')])

print('Compiling python bytecode...')
moduledir = sysconfig.get_path('purelib', vars={'base': str(prefix)})
compile_dir(destdir + path.join(moduledir, 'gtweak'), optimize=2)
