appdata_file = 'org.gnome.tweaks.appdata.xml'
i18n.merge_file(
  input: appdata_file + '.in',
  output: appdata_file,
  po_dir: '../po',
  install: true,
  install_dir: appdatadir
)

i18n.merge_file(
  input: configure_file(
    input: default_pkgappid + '.desktop.in',
    output: pkgappid + '.desktop.temp',
    configuration: defs_conf,
    install: false
  ),
  output: pkgappid + '.desktop',
  po_dir: '../po',
  install: true,
  install_dir: desktopdir,
  type: 'desktop'
)

gui_data = [
  'shell.ui',
  'shell.css'
]
install_data(gui_data, install_dir: pkgdatadir)

# Install the settings schema file
install_data(
  'org.gnome.tweaks.gschema.xml',
  install_dir: 'share/glib-2.0/schemas'
)

install_data (pkgappid + '.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'))
install_data (default_pkgappid + '-symbolic.svg', rename: pkgappid + '-symbolic.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'symbolic', 'apps'))
