project('gnome-tweaks',
  version: '3.29.92',
  meson_version: '>= 0.40.0'
)

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

install_data('gnome-tweaks', install_dir: bindir)
# Intentionally keep lid-inhibitor with old name so that user autostart
# files created by older versions of Tweaks will still work
install_data('gnome-tweak-tool-lid-inhibitor', install_dir: libexecdir)

subdir('data')
subdir('po')

meson.add_install_script('meson-postinstall.py')

defs_conf = configuration_data()
defs_conf.set('DATADIR', datadir)
defs_conf.set('GSETTINGSSCHEMADIR', schemadir)
defs_conf.set('LIBEXECDIR', libexecdir)
defs_conf.set('LOCALEDIR', localedir)
defs_conf.set('PKGDATADIR', pkgdatadir)
defs_conf.set('TWEAKDIR', join_paths(gtweakdir, 'tweaks'))
defs_conf.set('VERSION', meson.project_version())

configure_file(
  input: 'gtweak/defs.py.in',
  output: 'defs.py',
  configuration: defs_conf,
  install: true,
)

shell_sources = [
  'gtweak/app.py',
  'gtweak/egowrapper.py',
  'gtweak/gsettings.py',
  'gtweak/gshellwrapper.py',
  'gtweak/gtksettings.py',
  'gtweak/__init__.py',
  'gtweak/tweakmodel.py',
  'gtweak/tweakview.py',
  'gtweak/utils.py',
  'gtweak/widgets.py'
]

tweak_sources = [
  'gtweak/tweaks/__init__.py',
  'gtweak/tweaks/tweak_group_appearance.py',
  'gtweak/tweaks/tweak_group_desktop.py',
  'gtweak/tweaks/tweak_group_font.py',
  'gtweak/tweaks/tweak_group_general.py',
  'gtweak/tweaks/tweak_group_keymouse.py',
  'gtweak/tweaks/tweak_group_shell_extensions.py',
  'gtweak/tweaks/tweak_group_startup.py',
  'gtweak/tweaks/tweak_group_test.py',
  'gtweak/tweaks/tweak_group_title_bar.py',
  'gtweak/tweaks/tweak_group_top_bar.py',
  'gtweak/tweaks/tweak_group_windows.py',
  'gtweak/tweaks/tweak_group_workspaces.py',
  'gtweak/tweaks/tweak_group_xkb.py',
  'gtweak/tweaks/tweak_wacom.py',
]

install_data(shell_sources, install_dir: gtweakdir)
install_data(tweak_sources, install_dir: gtweakdir + '/tweaks')
