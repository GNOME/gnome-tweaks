AC_INIT([gnome-tweak-tool], [3.24.0], [https://bugzilla.gnome.org/enter_bug.cgi?product=gnome-tweak-tool])

AM_INIT_AUTOMAKE([foreign tar-ustar dist-xz no-dist-gzip])

AC_CONFIG_MACRO_DIR([m4])

AM_PATH_PYTHON([2.6])
GLIB_GSETTINGS

DESKTOP_SCHEMAS_REQUIRED_VERSION=3.23.3
GTK_REQUIRED_VERSION=3.12.0
PYGOBJECT_REQUIRED_VERSION=3.10

PKG_CHECK_MODULES([GSETTINGS_DESKTOP_SCHEMAS], [gsettings-desktop-schemas >= $DESKTOP_SCHEMAS_REQUIRED_VERSION])
PKG_CHECK_MODULES([GTK], [gtk+-3.0 >= $GTK_REQUIRED_VERSION])
PKG_CHECK_MODULES([PYGOBJECT3], [pygobject-3.0 >= $PYGOBJECT_REQUIRED_VERSION])

GETTEXT_PACKAGE=gnome-tweak-tool
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [GETTEXT package name])

AM_GNU_GETTEXT_VERSION([0.19.6])
AM_GNU_GETTEXT([external])

AS_AC_EXPAND(DATADIR, "${datadir}")
AS_AC_EXPAND(PKGDATADIR, "${datadir}/${PACKAGE}")
AS_AC_EXPAND(GSETTINGSSCHEMADIR, "${gsettingsschemadir}")
AS_AC_EXPAND(TWEAKDIR, "${pythondir}/gtweak/tweaks")
AS_AC_EXPAND(LOCALEDIR, "${localedir}")
AS_AC_EXPAND(LIBEXECDIR, "${libexecdir}")

AC_CONFIG_FILES([ po/Makefile.in
Makefile
data/Makefile
data/icons/Makefile
gtweak/defs.py
])
AC_OUTPUT
