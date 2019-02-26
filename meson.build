project('gnome-tweaks',
  version: '3.31.90',
  meson_version: '>= 0.46.0'
)

gnome = import('gnome')
i18n = import('i18n')
python = import('python')
py_installation = python.find_installation('python3')

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
libexecdir = join_paths(prefix, get_option('libexecdir'))
localedir = join_paths(prefix, get_option('localedir'))
pythondir = join_paths(prefix, py_installation.get_path('purelib'))

pkgdatadir = join_paths(datadir, meson.project_name())

appdatadir = join_paths(datadir, 'metainfo')
desktopdir = join_paths(datadir, 'applications')
gtweakdir = join_paths(pythondir, 'gtweak')
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
