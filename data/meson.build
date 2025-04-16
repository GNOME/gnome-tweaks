appdata_file = 'org.gnome.tweaks.appdata.xml'
appdata = i18n.merge_file(
  input: appdata_file + '.in',
  output: appdata_file,
  po_dir: '../po',
  install: true,
  install_dir: appdatadir
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test(
    'validate-metainfo', appstreamcli,
    args: [
      'validate', '--no-net', '--explain', appdata,
    ],
    depends: appdata,
  )
endif

desktop_file = i18n.merge_file(
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
# Validate Desktop file
desktop_file_validate = find_program('desktop-file-validate', required: false)
if desktop_file_validate.found()
  test(
    'desktop-file-validate',
    desktop_file_validate,
    args: [
      desktop_file,
    ],
    depends: desktop_file,
  )
endif

configure_file(
  input: default_pkgappid + '.service.in',
  output: pkgappid + '.service',
  configuration: defs_conf,
  install: true,
  install_dir: servicedir
)

gui_data = [
  'shell.ui',
  'tweaks.ui',
  'shell.css'
]
install_data(gui_data, install_dir: pkgdatadir)

# Install the settings schema file
install_data(
  'org.gnome.tweaks.gschema.xml',
  install_dir: 'share/glib-2.0/schemas'
)
# Validate GSchema
glib_compile_schemas = find_program('glib-compile-schemas', required: true)
if glib_compile_schemas.found()
  test(
    'validate-gschema', glib_compile_schemas,
    args: [
      '--strict', '--dry-run', meson.current_build_dir()
    ],
  )
endif

install_data (pkgappid + '.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'))
install_data (default_pkgappid + '-symbolic.svg', rename: pkgappid + '-symbolic.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'symbolic', 'apps'))
