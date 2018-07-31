defs_conf = configuration_data()
defs_conf.set('DATADIR', datadir)
defs_conf.set('GSETTINGSSCHEMADIR', schemadir)
defs_conf.set('LIBEXECDIR', libexecdir)
defs_conf.set('LOCALEDIR', localedir)
defs_conf.set('PKGDATADIR', pkgdatadir)
defs_conf.set('TWEAKDIR', join_paths(gtweakdir, 'tweaks'))
defs_conf.set('VERSION', meson.project_version())

configure_file(
  input: 'defs.py.in',
  output: 'defs.py',
  configuration: defs_conf,
  install: true,
  install_dir: gtweakdir
)

shell_sources = [
  'app.py',
  'egowrapper.py',
  'gsettings.py',
  'gshellwrapper.py',
  'gtksettings.py',
  '__init__.py',
  'tweakmodel.py',
  'tweakview.py',
  'utils.py',
  'widgets.py'
]

tweak_sources = [
  'tweaks/__init__.py',
  'tweaks/tweak_group_appearance.py',
  'tweaks/tweak_group_desktop.py',
  'tweaks/tweak_group_font.py',
  'tweaks/tweak_group_general.py',
  'tweaks/tweak_group_keymouse.py',
  'tweaks/tweak_group_shell_extensions.py',
  'tweaks/tweak_group_startup.py',
  'tweaks/tweak_group_test.py',
  'tweaks/tweak_group_title_bar.py',
  'tweaks/tweak_group_top_bar.py',
  'tweaks/tweak_group_windows.py',
  'tweaks/tweak_group_workspaces.py',
  'tweaks/tweak_group_xkb.py',
  'tweaks/tweak_wacom.py',
]

install_data(shell_sources, install_dir: gtweakdir)
install_data(tweak_sources, install_dir: gtweakdir + '/tweaks')
