#!/usr/bin/env python
# -*- coding: utf-8 -*-

import distutils.core
import distutils.command.build
import distutils.command.clean
import distutils.command.config
import distutils.command.install
import distutils.command.sdist
import distutils.util
import distutils.dir_util
import glob
import os
import stat
import sys
import traceback

sys.path.append('py')
sys.path.append('py/lib')
import qo
import Configuration
qo_export( Configuration.Configuration(), 'qocfg', False, 'Config' )

def cout( string ) :
	sys.stdout.write(string)
	sys.stdout.flush()
def cerr( string ) :
	sys.stderr.write(string)
	sys.stderr.flush()

class config( distutils.command.config.config ) :

	def error( self, reason ) :
		cerr( "ERROR: %s\r\n" % reason )
		sys.exit(1)

	def run( self ) :
		def version_dec( hexa ) :
			return ( (hexa & 0xff0000) >> 16, (hexa & 0x00ff00) >> 8, hexa & 0x0000ff )
		def version_hexa( maj, min = 0, rev = 0 ) :
			return maj << 16 | min << 8 | rev

		def has_pyqt3() :
			cout("Checking for PyQt3: ")
			ret = False
			try :
				import pyqtconfig
				pyqtver = pyqtconfig.Configuration().pyqt_version
				cout('.'.join(map( str, version_dec(pyqtver) )))
				if pyqtver >= version_hexa(3, 11) and pyqtver < version_hexa(4) :
					ret = True
					cout(" (ok)")
				else :
					cout(" (bad version)")
			except ImportError :
				cout("not found")
			except :
				cout("error ")
				traceback.print_exc()
			cout("\r\n")
			return ret


		# GUI
		gui = []
		if has_pyqt3() :
			gui.append("qt")
		if len(gui) == 0 :
			self.error("Qomics requires PyQt3")
		self.distribution.enabled_gui = gui
		self.distribution.packages += [ "qomics.ui.%s"%g for g in gui ]

		# gettext
		cout("Checking for msgfmt: ")
		msgfmt = qocfg.get_program( "msgfmt" )
		if msgfmt is not None :
			cout(msgfmt)
		else :
			cout("not found")
		cout("\r\n")
		if msgfmt is None :
			self.error("msgfmt (part of gettext) is needed for translation")


class build_po( distutils.core.Command ) :

	description = "build translation files"
	user_options = []

	def initialize_options( self ) :
		pass
	def finalize_options( self ) :
		pass

	def run( self ) :
		for po in glob.glob("po/*.po") :
			cmd = "msgfmt -c -o %s %s" % (po[:-2]+'mo',po)
			cout( cmd + "\n" )
			os.system(cmd)


class install_po( distutils.core.Command ) :

	description = "install translation files"
	user_options = [
		('install-dir=', 'd', "directory to install locale files to"),
	]

	def initialize_options( self ) :
		self.install_dir = None
	def finalize_options( self ) :
		self.set_undefined_options('install', ('install_locale','install_dir'))
	
	def get_outputs( self ) :
		return self.outputs

	def run( self ) :
		install_path = os.path.join(os.path.join(os.path.join(self.install_dir,"%s"),"LC_MESSAGES"),"qomics.mo")
		self.outputs = []
		for mo in glob.glob("po/*.mo") :
			d = install_path % os.path.basename(mo)[:-3]
			self.mkpath( os.path.dirname(d) )
			self.copy_file( mo, d )
			self.outputs.append( d )


class install_bin( distutils.core.Command ) :

	description = "install executables"
	user_options = []

	def initialize_options( self ) :
		pass
	def finalize_options( self ) :
		pass
	
	def get_outputs( self ) :
		return [ self.bin_file ]

	def run( self ) :
		install_base = self.get_finalized_command('install')
		exec_prefix = install_base.exec_prefix
		if install_base.root is not None :
			exec_prefix = distutils.util.change_root(install_base.root, exec_prefix)
		exec_prefix = os.path.join( exec_prefix, "bin" )

		python_exec = qocfg.get_program("pythonw") or "python"

		self.bin_file = os.path.join( exec_prefix, "qomics" )
		self.mkpath( os.path.dirname(self.bin_file) )
		o = open(self.bin_file,"w")
		o.write("#!/bin/sh\n")
		o.write("cd %s\n" % os.path.join( install_base.install_lib_noroot, "qomics" ) )
		o.write("%s -O $PWD/qomics.py $@\n"%python_exec)
		o.close()
		mode = ((os.stat(self.bin_file)[stat.ST_MODE]) | 0555) & 07777
		os.chmod(self.bin_file, mode)



class build( distutils.command.build.build ) :
	def run( self ) :
		self.run_command('config')
		distutils.command.build.build.run( self )

		sysconfig_file = os.path.join(os.path.join(self.build_lib,"qomics"),"sysconfig.py")
		o = open(sysconfig_file,"w")
		o.write( "GUI = [ %s ]\n" % ','.join(["'%s'"%g for g in self.distribution.enabled_gui]) )
		o.write( "GUI_default = GUI[0]\n" )
		o.close()

	def has_po( self ) :
		return len(glob.glob("po/*.po")) > 0
	sub_commands = distutils.command.build.build.sub_commands + [
		('build_po',has_po),
	]


datadir = "share"
pkgdatadir = os.path.join(datadir,"qomics")

class install( distutils.command.install.install ) :

	user_options = distutils.command.install.install.user_options + [
		('install-locale',None,"installation directory for locale"),
	]

	def initialize_options( self ) :
		distutils.command.install.install.initialize_options( self )
		self.install_locale = None
	def finalize_unix( self ) :
		distutils.command.install.install.finalize_unix( self )
		self.install_locale = os.path.join( os.path.join(self.install_data,'share'), 'locale' )
	def finalize_other( self ) :
		distutils.command.install.install.finalize_other( self )
		self.install_locale = os.path.join( os.path.join(self.install_lib,'qomics'), 'locale' )
	def finalize_options( self ) :
		distutils.command.install.install.finalize_options( self )
		if self.root is not None :
			self.change_roots('locale')
		else :
			for attr in [ 'locale','data', 'lib' ] :
				setattr( self, "install_%s_noroot"%attr, getattr( self, "install_%s"%attr ) )

	def expand_dirs( self ) :
		distutils.command.install.install.expand_dirs( self )
		self._expand_attrs( ['install_locale'] )
	def change_roots( self, *attrs ) :
		for attr in attrs :
			setattr( self, "install_%s_noroot"%attr, getattr( self, "install_%s"%attr ) )
		distutils.command.install.install.change_roots( self, *attrs )

	def run( self ) :
		distutils.command.install.install.run( self )
		# append install configuration to sysconfig
		sysconfig_file = os.path.join( os.path.join(self.install_lib,'qomics'), 'sysconfig.py' )
		o = open(sysconfig_file,"a")
		for name, value in [ 
			('LOCALEDIR',self.install_locale_noroot), 
			('PKGDATADIR',os.path.join(self.install_data_noroot,pkgdatadir)),
			] :
			o.write( "%s = \"%s\"\n" % (name,value) )
		o.close()
	
	def get_outputs( self ) :
		sysconfig_file = os.path.join( os.path.join(self.install_lib,'qomics'), 'sysconfig.py' )
		return distutils.command.install.install.get_outputs( self ) + [ sysconfig_file, sysconfig_file + 'c' ]

	def has_po( self ) :
		return len(glob.glob("po/*.mo")) > 0
	def has_bin( self ) :
		return not sys.platform.startswith('win')
	sub_commands = distutils.command.install.install.sub_commands + [
		('install_po',has_po),
		('install_bin',has_bin),
	]

class clean( distutils.command.clean.clean ) :
	def run( self ) :
		distutils.command.clean.clean.run( self )
		map( os.unlink, glob.glob("po/*.mo") )
	

def get_extra_version() :
	ev = qocfg.APPLICATION["extra_version"]
	if ev[0] == "r" :
		return "-"+ev[1:]
	else :
		return "_"+ev


class sdist( distutils.command.sdist.sdist ) :

	default_format = { "posix" : "bztar" }

	def finalize_options( self ) :
		if self.dist_dir is None :
			self.dist_dir = os.getenv("QOMICS_DOWNLOAD")
		distutils.command.sdist.sdist.finalize_options( self )

	def make_distribution( self ) :
		base_dir = self.distribution.get_fullname() + get_extra_version()
		base_name = os.path.join(self.dist_dir, base_dir)

		self.make_release_tree(base_dir, self.filelist.files)
		archive_files = []              # remember names of files we create
		for fmt in self.formats:
			file = self.make_archive(base_name, fmt, base_dir=base_dir)
			archive_files.append(file)

		self.archive_files = archive_files

		if not self.keep_temp:
			distutils.dir_util.remove_tree(base_dir, dry_run=self.dry_run)


class release( distutils.core.Command ) :

	description = "release Qomics"
	user_options = [
		('dist-dir', 'd', "distribution directory"),
	]

	def initialize_options( self ) :
		self.dist_dir = None
	def finalize_options( self ) :
		if self.dist_dir is None :
			self.dist_dir = os.getenv("QOMICS_DOWNLOAD")
	def run( self ) :
		version = qocfg.APPLICATION["version"]
		release = qocfg.APPLICATION["extra_version"]
		if release[0] != 'r' :
			raise Exception("not a release: %s"%release)
		release = release[1:]
		int(release)
		print "Qomics %s release %s" % (version,release)
		print "output=%s" % self.dist_dir

		# ebuild
		ebuild = "dist/gentoo/qomics-%s-r%s.ebuild" % (version,release)
		if not os.path.exists( ebuild ) :
			os.system( "svn mv %s %s" % (glob.glob("dist/gentoo/qomics-*.ebuild")[0], ebuild) )

		# windows

		# debian

		# rpm

		# source
		self.get_finalized_command('sdist').dist_dir = self.dist_dir
		self.run_command('sdist')


distutils.core.setup(
	name = "qomics",
	version = qocfg.APPLICATION["version"],
	description = "A comic strip collection manager.",
	author = "PaulevГ© LoГЇc aka Panard",
	author_email = "panard@inzenet.org",
	url = "http://qomics.inzenet.org",
	license = "GPL-2",

	package_dir = {'qomics': 'py'},
	packages = [ 
		'qomics',
		'qomics.qo',
		'qomics.ext',
		'qomics.ext.OpenDocument',
		'qomics.lib',
		'qomics.ui',
	],

	data_files = [
		(os.path.join(pkgdatadir,'gfx'), glob.glob('gfx/*.png') + glob.glob('gfx/*.xml')),
		(os.path.join(pkgdatadir,'dtd'), glob.glob('dtd/*.dtd')),
	],

	cmdclass = {
		'config': config,
		'build': build,
		'build_po' : build_po,
		'install': install,
		'install_po' : install_po,
		'install_bin' : install_bin,
		'clean' : clean,
		'release' : release,
		'sdist' : sdist,
	},
)

