bin_SCRIPTS = \
	gnome-tweak-tool

#nobase means gtweak dir is preserved in site-packages
appdir = $(pythondir)
nobase_dist_app_PYTHON = \
	$(wildcard $(srcdir)/gtweak/*.py) \
	$(wildcard $(srcdir)/gtweak/tweaks/*.py)

guidir = $(pkgdatadir)
gui_DATA = \
	data/shell.ui \
	data/welcome.png

desktopdir = $(datadir)/applications
desktop_DATA = data/gnome-tweak-tool.desktop

EXTRA_DIST = \
	$(bin_SCRIPTS) \
	$(gui_DATA) \
	$(desktop_DATA)

CLEANFILES = \
	$(wildcard $(srcdir)/gtweak/*.pyc) \
	$(wildcard $(srcdir)/gtweak/tweaks/*.pyc)

DISTCLEANFILES = \
	gtweak/defs.py
