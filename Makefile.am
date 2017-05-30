bin_SCRIPTS = \
	gnome-tweak-tool

libexec_SCRIPTS = \
	gnome-tweak-tool-lid-inhibitor

#nobase means gtweak dir is preserved in site-packages
appdir = $(pythondir)
nobase_dist_app_PYTHON = \
	$(wildcard $(srcdir)/gtweak/*.py) \
	$(wildcard $(srcdir)/gtweak/tweaks/*.py)

nobase_app_PYTHON = gtweak/defs.py

EXTRA_DIST = \
	$(bin_SCRIPTS) \
	$(libexec_SCRIPTS)

CLEANFILES = \
	$(wildcard $(srcdir)/gtweak/*.pyc) \
	$(wildcard $(srcdir)/gtweak/tweaks/*.pyc)

DISTCLEANFILES = \
	gtweak/defs.py

SUBDIRS = data po

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
