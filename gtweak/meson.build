defs_conf = configuration_data()
defs_conf.set('DATADIR', datadir)
defs_conf.set('GSETTINGSSCHEMADIR', schemadir)
defs_conf.set('LIBEXECDIR', libexecdir)
defs_conf.set('LOCALEDIR', localedir)
defs_conf.set('PKGDATADIR', pkgdatadir)
defs_conf.set('BINDIR', bindir)
defs_conf.set('APPID', pkgappid)
defs_conf.set('TWEAKDIR', join_paths(gtweakdir, 'tweaks'))
defs_conf.set('VERSION', meson.project_version())
defs_conf.set('PROFILE', get_option('profile'))

configure_file(
  input: 'defs.py.in',
  output: 'defs.py',
  configuration: defs_conf,
  install_dir: gtweakdir
)

shell_sources = [
  'app.py',
  'devicemanager.py',
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
  'tweaks/tweak_group_sound.py',
  'tweaks/tweak_group_font.py',
  'tweaks/tweak_group_mouse.py',
  'tweaks/tweak_group_keyboard.py',
  'tweaks/tweak_group_startup.py',
  'tweaks/tweak_group_windows.py'
]

python3.install_sources(shell_sources, subdir: 'gtweak')
python3.install_sources(tweak_sources, subdir: join_paths('gtweak', 'tweaks'))
