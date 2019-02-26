project('gnome-tweaks',
  version: '3.34.0',
  meson_version: '>= 0.46.0'
)

gnome = import('gnome')
i18n = import('i18n')
python = import('python')
python3 = python.find_installation('python3')

if not python3.found()
    error('No valid python3 installation found!')
endif

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
libexecdir = join_paths(prefix, get_option('libexecdir'))
localedir = join_paths(prefix, get_option('localedir'))
pythondir = join_paths(prefix, python3.get_path('purelib'))

pkgdatadir = join_paths(datadir, meson.project_name())

appdatadir = join_paths(datadir, 'metainfo')
desktopdir = join_paths(datadir, 'applications')
gtweakdir = python3.get_install_dir(subdir: 'gtweak')
icondir = join_paths(datadir, 'icons', 'hicolor')
schemadir = join_paths(datadir, 'glib-2.0', 'schemas')

install_data('gnome-tweaks', install_dir: bindir)
# Intentionally keep lid-inhibitor with old name so that user autostart
# files created by older versions of Tweaks will still work
install_data('gnome-tweak-tool-lid-inhibitor', install_dir: libexecdir)

subdir('gtweak')
subdir('data')
subdir('po')

meson.add_install_script('meson-postinstall.py')
