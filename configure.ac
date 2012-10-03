AC_INIT([gnome-tweak-tool], [3.6.0], [john.stowers@gmail.com])

AM_INIT_AUTOMAKE([foreign tar-ustar dist-xz no-dist-gzip])

AM_PATH_PYTHON([2.6])
GLIB_GSETTINGS

DESKTOP_SCHEMAS_REQUIRED_VERSION=3.4.0
PYGOBJECT_REQUIRED_VERSION=3.2.1

PKG_CHECK_MODULES([GSETTINGS_DESKTOP_SCHEMAS], [gsettings-desktop-schemas >= $DESKTOP_SCHEMAS_REQUIRED_VERSION])
PKG_CHECK_MODULES([PYGOBJECT3], [pygobject-3.0 >= $PYGOBJECT_REQUIRED_VERSION],,
    [PKG_CHECK_MODULES([PYGOBJECT2], [pygobject-2.0 >= 2.28.0])])

AC_CHECK_PROG(GCONFTOOL,gconftool-2,gconftool-2,no)
if test "$GCONFTOOL" = no ; then
	AC_MSG_ERROR(Cannot find gconftool-2)
fi

IT_PROG_INTLTOOL([0.40.0])
AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_VERSION([0.17])
GETTEXT_PACKAGE=gnome-tweak-tool
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [GETTEXT package name])

AS_AC_EXPAND(DATADIR, "${datadir}")
AS_AC_EXPAND(PKGDATADIR, "${datadir}/${PACKAGE}")
AS_AC_EXPAND(GSETTINGSSCHEMADIR, "${gsettingsschemadir}")
AS_AC_EXPAND(TWEAKDIR, "${pythondir}/gtweak/tweaks")
AS_AC_EXPAND(LOCALEDIR, "${localedir}")

AC_CONFIG_FILES([ po/Makefile.in
Makefile
data/Makefile
data/icons/Makefile
gtweak/defs.py
])
AC_OUTPUT
