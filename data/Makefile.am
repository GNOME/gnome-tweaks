SUBDIRS = icons

guidir = $(pkgdatadir)
gui_DATA = \
	shell.ui \
	shell.css

desktop_in_files = gnome-tweak-tool.desktop.in
desktopdir = $(datadir)/applications
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST = \
	gnome-tweak-tool.appdata.xml \
	$(gui_DATA) \
	$(desktop_in_files)

CLEANFILES = \
	$(desktop_DATA)

