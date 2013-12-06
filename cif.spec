%define		cifver		1.0.3
%define		cifrel		0
%define		cifdevrel	alpha3
%define		cifgittag	v1.0.3-alpha.2-2
%define		cifprefix	/opt/cif
%define		cifhome		%{cifprefix}
%define		cifbin		%{cifprefix}/bin
%define		ciflib		%{cifprefix}/lib
%define		cifetc		%{cifprefix}/etc
%define		cifmodules	libcif libcif-dbi cif-router cif-smrt

Name:		cif
Version:	%{cifver}
Release:	%{cifrel}%{?cifdevrel:.%{cifdevrel}}%{?dist}
Summary:	Collective Intelligence Framework

Group:		Applications/CIF
License:	LGPL
URL:		https://code.google.com/p/collective-intelligence-framework/
Source0:	http://collective-intelligence-framework.googlecode.com/files/cif-v1%{?cifgittag:-%{cifgittag}}.tar.gz

BuildArch:	noarch

# Spec requirements to build
BuildRequires:	/usr/bin/getent
BuildRequires:	/usr/bin/id
BuildRequires:	/usr/bin/install
BuildRequires:	/usr/sbin/useradd
BuildRequires:	/usr/sbin/usermod

# Base Requirements (per documentation)
Requires:       /usr/bin/rsync
Requires:       /usr/bin/wget
Requires:       /usr/sbin/ntpdate
Requires:       bind
Requires:       bind-utils
Requires:       httpd
Requires:       mod_perl
Requires:       mod_ssl
Requires:       postgresql-server
Requires:       rng-tools

Requires:	perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       perl(Apache2::RequestRec) >= 2.0.4
Requires:       perl(Class::Accessor) >= 0.34
Requires:       perl(Class::DBI) >= 3.0.17
Requires:	perl(Class::Trigger) >= 0.14
Requires:       perl(Compress::Snappy) >= 0.18
Requires:       perl(Config::Simple) >= 4.59
Requires:       perl(DBD::Pg) >= 1.43
Requires:       perl(DBI) >= 1.37
Requires:       perl(Date::Manip) >= 6.11
Requires:       perl(DateTime) >= 0.42
Requires:       perl(DateTime::Format::DateParse) >= 0.05
Requires:       perl(Digest::MD5) >= 2.27
Requires:       perl(Digest::SHA) >= 2.10
Requires:       perl(Encode) >= 2.23
Requires:	perl(File::Spec) >= 0.8
Requires:       perl(File::Type) >= 0.22
Requires:       perl(Google::ProtocolBuffers) >= 0.08
Requires:       perl(IO::Uncompress::Unzip) >= 2.02
Requires:       perl(Iodef::Pb::Simple) >= 0.21
Requires:       perl(LWP::Protocol::https) >= 6.03
Requires:       perl(LWP::UserAgent) >= 6.02
Requires:	perl(LWPx::ParanoidAgent) >= 1.10
Requires:       perl(Linux::Cpuinfo) >= 1.7
Requires:       perl(Log::Dispatch) >= 2.32
Requires:       perl(MIME::Base64) >= 3.06
Requires:       perl(MIME::Lite) >= 3.027
Requires:       perl(Module::Pluggable) >= 3.9
Requires:       perl(Net::Abuse::Utils) >= 0.23
Requires:       perl(Net::Abuse::Utils::Spamhaus) >= 0.05
Requires:       perl(Net::DNS::Match) >= 0.05
Requires:       perl(Net::Patricia) >= 1.16
Requires:       perl(Net::SSLeay) >= 1.43
Requires:       perl(OSSP::uuid) >= 1.5.1
Requires:       perl(Regexp::Common) >= 2.122
Requires:       perl(Regexp::Common::net::CIDR) >= 0.02
Requires:       perl(Sys::MemInfo) >= 0.91
Requires:       perl(Text::CSV) >= 1.18
Requires:       perl(Time::HiRes) >= 1.9719
Requires:       perl(Try::Tiny) >= 0.04
Requires:       perl(URI::Escape) >= 1.56
Requires:       perl(XML::RSS) >= 1.48
Requires:       perl(ZeroMQ) >= 0.21

# Setup Perl dependency filters
%{?filter_setup:
%filter_from_requires /perl(CIF)/d
%filter_from_requires /perl(CIF::.*)/d
%filter_provides_in %{ciflib}/.*$
%filter_setup
}
%{?perl_default_filter}

%description
CIF is a cyber threat intelligence management system. CIF allows you to combine known malicious threat information from 
many sources and use that information for identification (incident response), detection (IDS) and mitigation 
(null route). The most common types of threat intelligence warehoused in CIF are IP addresses, domains and urls that 
are observed to be related to malicious activity.

This framework pulls in various data-observations from any source; create a series of messages "over time" 
(eg: reputation). When you query for the data, you'll get back a series of messages chronologically and make 
decisions much as you would look at an email thread, a series of observations about a particular bad-actor.

CIF helps you to parse, normalize, store, post process, query, share and produce data sets of threat intelligence.

The original idea came from from:

http://bret.appspot.com/entry/how-friendfeed-uses-mysql 

%pre
/usr/bin/getent passwd cif 2>&1 >/dev/null || /usr/sbin/useradd -r -M -d %{cifhome} cif

%post
if [ "$1" -eq "1" ] ; then 
	/usr/sbin/usermod -a -G cif apache
fi

%prep
%setup -qn cif-v1%{?cifgittag:-%{cifgittag}}

%build
#./configure --prefix=%{cifprefix}
#make %{?_smp_mflags}

%install
rm -rf %{buildroot}

# Create base directory structure
%{__mkdir} -p %{buildroot}%{cifprefix}
%{__mkdir} -p %{buildroot}%{ciflib}
%{__mkdir} -p %{buildroot}%{cifbin}
%{__mkdir} -p %{buildroot}%{cifetc}
%{__mkdir} -p %{buildroot}%{cifprefix}/scripts
%{__mkdir} -p %{buildroot}%{cifprefix}/schemas
%{__mkdir} -p %{buildroot}%{cifprefix}/cache
%{__mkdir} -p %{buildroot}%{cifprefix}/certs
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/cif

# Do not use upstream's installer since it is not suitable for packaging at this time
# make install DESTDIR=%{buildroot}

# Modules and directories to package
set +x
MODULES=". %{cifmodules}"
MODDIRS="bin schemas lib rules/etc"
SCRIPTDIR="scripts"

# Over each module...
for module in $MODULES ; do
	echo "Processing $module..."
	# Check for the existance of each MODDIR
	for moddir in $MODDIRS ; do
		echo "- $moddir"
		if [ -e "$module/$moddir" ] ; then
			# Install each file from the module to the buildroot
			( cd "$module/$moddir" && find * -type f ) | while read file ; do
				echo "+ %{__install} -D $module/$moddir/$file %{buildroot}%{cifprefix}/$(basename $moddir)/$file"
				%{__install} -D "$module/$moddir/$file" "%{buildroot}%{cifprefix}/$(basename $moddir)/$file"
			done
		fi
	done
	# Check for scripts to be installed for the current distribution
	if [ -e "$module/$SCRIPTDIR" ] ; then
		echo "- $SCRIPTDIR"
		if [ -e "$module/$SCRIPTDIR/%{?rhel:el%{rhel}}%{?fedora:fedora}" ] ; then
			( cd "$module/$SCRIPTDIR/%{?rhel:el%{rhel}}%{?fedora:fedora}" && find * -type f ) | while read file ; do
				echo "%{__install} -D $module/$SCRIPTDIR/%{?rhel:el%{rhel}}%{?fedora:fedora}/$file %{buildroot}%{cifprefix}/$SCRIPTDIR/$file"
				%{__install} -D "$module/$SCRIPTDIR/%{?rhel:el%{rhel}}%{?fedora:fedora}/$file" "%{buildroot}%{cifprefix}/$SCRIPTDIR/$file"
			done
		fi
		# Install the CIF configuration file in %{cifprefix} and link to %{cifhome}
		if [ -e "$module/$SCRIPTDIR/cif.conf" ] ; then
			echo "%{__install} $module/$SCRIPTDIR/cif.conf %{buildroot}%{cifprefix}/"
			%{__install} "$module/$SCRIPTDIR/cif.conf" "%{buildroot}%{cifprefix}/"
			echo "%{__ln_s} -T cif.conf %{buildroot}%{cifhome}/.cif"
			%{__ln_s} -T cif.conf %{buildroot}%{cifhome}/.cif
		fi
	fi
done
set -x

%clean
rm -rf %{buildroot}

%files
%defattr(664,cif,cif,775)
%dir %{cifprefix}
%{ciflib}
%dir %{cifbin}
%attr(775,cif,cif) %{cifbin}/*
%dir %{cifetc}
%config(noreplace) %attr(660,cif,cif) %{cifetc}/*
%{cifprefix}/schemas
%{cifprefix}/scripts
%config(noreplace) %{cifprefix}/cif.conf
%config(noreplace) %{cifhome}/.cif
%dir %{cifprefix}/certs
%dir %{cifprefix}/cache
%dir %{_localstatedir}/log/cif

%changelog
* Fri Dec 06 2013 Aaron K Reffett <akreffett@cert.org> 1.0.1-1
- Updated to release 1.0.1

* Tue Jun 18 2013 Aaron K Reffett <akreffett@cert.org> 1.0.0-0.rc3.1.2.4
- Updated to latest CIF
- Various bug fixes

* Thu Jun 13 2013 Aaron K Reffett <akreffett@cert.org> 1.0.0-0.rc3.1.2
- Updated to latest cif-v1 upstream
- Added cache and certs directories to build

* Fri Apr 26 2013 Aaron K Reffett <akreffett@cert.org> 1.0.0-0.rc2.2.11
- Updated to latest cif-v1 in all submodules

* Fri Mar 29 2013 Aaron K Reffett <akreffett@cert.org> 1.0.0-0.rc2.2.6
- Spec tweak to reduce noise
- Included skeleton configuration files for httpd and postgres
- Included scripts for initializing the database
- Included postgres tuning helper scripts from documentation
- Included model cif.conf
- Initial build

