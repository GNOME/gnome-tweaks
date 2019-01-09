appdata_file = 'org.gnome.tweaks.appdata.xml'
i18n.merge_file(appdata_file,
  input: appdata_file + '.in',
  output: appdata_file,
  po_dir: '../po',
  install: true,
  install_dir: appdatadir
)
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test(
    'validate-appdata', appstream_util,
    args: [
      'validate-relax', appdata_file.full_path()
    ]
  )
endif

desktop_file = 'org.gnome.tweaks.desktop'
i18n.merge_file(desktop_file,
  input: desktop_file + '.in',
  output: desktop_file,
  po_dir: '../po',
  install: true,
  install_dir: desktopdir,
  type: 'desktop'
)
desktop_file_validate = find_program('desktop-file-validate', required: false)
if desktop_file_validate.found()
  test(
    'validate-desktop',
    desktop_file_validate,
    args: [
      desktop_file.full_path()
    ]
  )
endif

gui_data = [
  'shell.ui',
  'shell.css'
]
install_data(gui_data, install_dir: pkgdatadir)

install_data ('org.gnome.tweaks.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'))
install_data ('org.gnome.tweaks-symbolic.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'symbolic', 'apps'))
