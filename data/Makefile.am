SUBDIRS = icons

guidir = $(pkgdatadir)
gui_DATA = \
	shell.ui \
	shell.css

desktop_in_files = gnome-tweak-tool.desktop.in
desktopdir = $(datadir)/applications
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

@INTLTOOL_XML_RULE@
appdatadir = $(datadir)/appdata
appdata_in_files = gnome-tweak-tool.appdata.xml.in
appdata_DATA = $(appdata_in_files:.xml.in=.xml)

EXTRA_DIST = \
	$(appdata_in_files) \
	$(gui_DATA) \
	$(desktop_in_files)

CLEANFILES = \
	$(desktop_DATA) \
	$(appdata_DATA)
