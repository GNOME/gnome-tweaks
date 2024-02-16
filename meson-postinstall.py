#!/usr/bin/env python3

import sysconfig
from compileall import compile_dir
from os import environ, path

prefix = environ.get('MESON_INSTALL_PREFIX', '/usr/local')
destdir = environ.get('DESTDIR', '')

print('Compiling python bytecode...')
moduledir = sysconfig.get_path('purelib', vars={'base': str(prefix)})
compile_dir(destdir + path.join(moduledir, 'gtweak'), optimize=2)
