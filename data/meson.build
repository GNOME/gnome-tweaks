appdata_file = i18n.merge_file(
  'appdata',
  input: project_id + '.appdata.xml.in',
  output: project_id + '.appdata.xml',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: appdatadir
)
appstream_util = find_program(['appstream-util'], required: false)
if appstream_util.found()
  test (
    'Validate appdata file',
    appstream_util,
    args: ['validate', '--nonet', appdata_file.full_path()]
  )
endif
desktop_file = i18n.merge_file(
  'desktop',
  input: project_id + '.desktop.in',
  output: project_id + '.desktop',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: desktopdir,
  type: 'desktop'
)
desktop_file_validate = find_program('desktop-file-validate', required:false)
if desktop_file_validate.found()
  test (
    'Validate desktop file',
    desktop_file_validate,
    args: desktop_file.full_path()
  )
endif


gui_data = [
  'shell.ui',
  'shell.css'
]
install_data(gui_data, install_dir: pkgdatadir)

install_data (project_id + '.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'))
install_data (project_id + '-symbolic.svg',
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'symbolic', 'apps'))
