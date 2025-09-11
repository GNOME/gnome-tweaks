project('gnome-tweaks',
  version: '49.0',
  meson_version: '>= 0.59.0'
)

gnome = import('gnome')
i18n = import('i18n')
python = import('python')
python3 = python.find_installation('python3')

if not python3.found()
    error('No valid python3 installation found!')
endif

# Tweaks requires at least Python 3.10 for certain type annotations
if not python3.language_version().version_compare('>= 3.10')
  error('Python 3.10 or newer is required.')
endif

# Declare runtime dependency versions here to make packaging more obvious
dependency('glib-2.0', version: '>= 2.78.0')
dependency('gobject-introspection-1.0', version: '>= 1.78.0')
dependency('gtk4', version: '>= 4.10.0')
dependency('libadwaita-1', version: '>= 1.4.0')
dependency('pygobject-3.0', version: '>= 3.46.0')
dependency('gudev-1.0', version: '>= 238')
dependency('gsettings-desktop-schemas', version: '>= 46.0')

prefix = get_option('prefix')

bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
libexecdir = join_paths(prefix, get_option('libexecdir'))
localedir = join_paths(prefix, get_option('localedir'))
pythondir = join_paths(prefix, python3.get_path('purelib'))

pkgdatadir = join_paths(datadir, meson.project_name())

default_pkgappid = 'org.gnome.tweaks'
pkgappid = default_pkgappid

appdatadir = join_paths(datadir, 'metainfo')
desktopdir = join_paths(datadir, 'applications')
gtweakdir = python3.get_install_dir(subdir: 'gtweak')
icondir = join_paths(datadir, 'icons', 'hicolor')
schemadir = join_paths(datadir, 'glib-2.0', 'schemas')
servicedir = join_paths(datadir, 'dbus-1', 'services')

install_data('gnome-tweaks', install_dir: bindir)

subdir('gtweak')
subdir('data')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)

meson.add_install_script('meson-postinstall.py')
