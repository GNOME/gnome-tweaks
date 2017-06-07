project('gnome-tweak-tool', 'c',
  version: '3.25.2',
  meson_version: '>= 0.40.0'
)

gtk_req = '>= 3.12.0'
pygobject_req = '>= 3.10'
schemas_req = '>= 3.23.3'

gnome = import('gnome')
i18n = import('i18n')
python3 = import('python3')

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
libexecdir = join_paths(prefix, get_option('libexecdir'))
localedir = join_paths(prefix, get_option('localedir'))
pythondir = join_paths(prefix, python3.sysconfig_path('purelib'))

pkgdatadir = join_paths(datadir, meson.project_name())

appdatadir = join_paths(datadir, 'metainfo')
desktopdir = join_paths(datadir, 'applications')
gtweakdir = join_paths(pythondir, 'gtweak')
icondir = join_paths(datadir, 'icons', 'hicolor')
schemadir = join_paths(datadir, 'glib-2.0', 'schemas')

gtk_dep = dependency('gtk+-3.0', version: gtk_req)
pygobject_dep = dependency('pygobject-3.0', version: pygobject_req)
schemas_dep = dependency('gsettings-desktop-schemas', version: schemas_req)

install_data('gnome-tweak-tool', install_dir: bindir)
install_data('gnome-tweak-tool-lid-inhibitor', install_dir: libexecdir)

subdir('gtweak')
subdir('data')
subdir('po')

meson.add_install_script('meson-postinstall.sh')