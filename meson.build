project('gnome-tweaks',
  version: '45.alpha',
  meson_version: '>= 0.50.0'
)

gnome = import('gnome')
i18n = import('i18n')
python = import('python')
python3 = python.find_installation('python3')

if not python3.found()
    error('No valid python3 installation found!')
endif

dependency('libhandy-1', version: '>=1.5')

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
libexecdir = join_paths(prefix, get_option('libexecdir'))
localedir = join_paths(prefix, get_option('localedir'))
pythondir = join_paths(prefix, python3.get_path('purelib'))

pkgdatadir = join_paths(datadir, meson.project_name())

default_pkgappid = 'org.gnome.tweaks'
pkgappid = default_pkgappid

if get_option('profile') == 'development'
  pkgappid = 'org.gnome.TweaksDevel'
endif

appdatadir = join_paths(datadir, 'metainfo')
desktopdir = join_paths(datadir, 'applications')
gtweakdir = python3.get_install_dir(subdir: 'gtweak')
icondir = join_paths(datadir, 'icons', 'hicolor')
schemadir = join_paths(datadir, 'glib-2.0', 'schemas')

install_data('gnome-tweaks', install_dir: bindir)

subdir('gtweak')
subdir('data')
subdir('po')

meson.add_install_script('meson-postinstall.py')
