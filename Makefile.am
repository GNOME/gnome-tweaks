bin_SCRIPTS = \
	gnome-tweak-tool

libexec_SCRIPTS = \
	gnome-tweak-tool-lid-inhibitor

gnome-tweak-tool-lid-inhibitor: gnome-tweak-tool-lid-inhibitor.in Makefile
	$(AM_V_GEN)sed -e s!\@PYTHON\@!@PYTHON@! < $< > $@
	chmod +x $@

#nobase means gtweak dir is preserved in site-packages
appdir = $(pythondir)
nobase_dist_app_PYTHON = \
	$(wildcard $(srcdir)/gtweak/*.py) \
	$(wildcard $(srcdir)/gtweak/tweaks/*.py)

nobase_app_PYTHON = gtweak/defs.py

EXTRA_DIST = \
	$(bin_SCRIPTS) \
	gnome-tweak-tool-lid-inhibitor.in

CLEANFILES = \
	$(wildcard $(srcdir)/gtweak/*.pyc) \
	$(wildcard $(srcdir)/gtweak/tweaks/*.pyc)

DISTCLEANFILES = \
	gtweak/defs.py \
	gnome-tweak-tool-lid-inhibitor

SUBDIRS = data po

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
