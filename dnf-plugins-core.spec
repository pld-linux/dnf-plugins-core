#
# Conditional build:
%bcond_without	yum_compatibility	# Add yum plugins provides
%bcond_without	yum_utils		# Build yum-utils replacement package dnf-utils
#
Summary:	Core Plugins for DNF
Name:		dnf-plugins-core
Version:	4.0.19
Release:	3
License:	GPL v2+
Source0:	https://github.com/rpm-software-management/dnf-plugins-core/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	ab4a9b6919a70943d45404943ae49a21
Patch0:		install.patch
Patch1:		migrate3.patch
URL:		https://github.com/rpm-software-management/dnf-plugins-core
BuildRequires:	cmake
BuildRequires:	dnf >= 4.2.22
BuildRequires:	gettext
BuildRequires:	python3-dbus
BuildRequires:	python3-devel
BuildRequires:	python3-nose
BuildRequires:	sphinx-pdg
Requires:	dnf >= 4.2.22
Requires:	python3-dateutil
Requires:	python3-dbus
Requires:	python3-hawkey >= 0.46.1
%if %{with yum_compatibility}
Provides:	yum-plugin-auto-update-debug-info = %{version}-%{release}
Provides:	yum-plugin-changelog = %{version}-%{release}
Provides:	yum-plugin-copr = %{version}-%{release}
%endif
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Core Plugins for DNF. This package enhances DNF with builddep,
config-manager, copr, debug, debuginfo-install, download,
needs-restarting, groups-manager, repoclosure, repograph, repomanage,
reposync, changelog and repodiff commands. Additionally provides
generate_completion_cache passive plugin.

%package -n dnf-utils
Summary:	Yum-utils CLI compatibility layer
Requires:	%{name} = %{version}-%{release}
Provides:	yum-utils = %{version}-%{release}

%description -n dnf-utils
As a Yum-utils CLI compatibility layer, supplies in CLI shims for
debuginfo-install, repograph, package-cleanup, repoclosure,
repomanage, repoquery, reposync, repotrack, repodiff, builddep,
config-manager, debug, download and yum-groups-manager that use new
implementations using DNF.

%package -n dnf-plugin-leaves
Summary:	Leaves Plugin for DNF
Requires:	%{name} = %{version}-%{release}

%description -n dnf-plugin-leaves
Leaves Plugin for DNF. List all installed packages not required by any
other installed package.

%package -n dnf-plugin-local
Summary:	Local Plugin for DNF
Requires:	%{name} = %{version}-%{release}
Requires:	createrepo_c

%description -n dnf-plugin-local
Local Plugin for DNF. Automatically copy all downloaded packages to a
repository on the local filesystem and generating repo metadata.

%package -n dnf-plugin-migrate
Summary:	Migrate Plugin for DNF
Requires:	%{name} = %{version}-%{release}
Requires:	yum

%description -n dnf-plugin-migrate
Migrate Plugin for DNF. Migrates history, group and yumdb data from
yum to dnf.

%package -n dnf-plugin-post-transaction-actions
Summary:	Post transaction actions Plugin for DNF
Requires:	%{name} = %{version}-%{release}

%description -n dnf-plugin-post-transaction-actions
Post transaction actions Plugin for DNF. Plugin runs actions (shell
commands) after transaction is completed. Actions are defined in
action files.

%package -n dnf-plugin-show-leaves
Summary:	Show-leaves Plugin for DNF
Requires:	%{name} = %{version}-%{release}
Requires:	dnf-plugin-leaves = %{version}-%{release}

%description -n dnf-plugin-show-leaves
Show-leaves Plugin for DNF. List all installed packages that are no
longer required by any other installed package after a transaction.

%package -n dnf-plugin-versionlock
Summary:	Version Lock Plugin for DNF
Requires:	%{name} = %{version}-%{release}
%if %{with yum_compatibility}
Provides:	yum-plugin-versionlock = %{version}-%{release}
%endif

%description -n dnf-plugin-versionlock
Version lock plugin takes a set of name/versions for packages and
excludes all other versions of those packages. This allows you to e.g.
protect packages from being updated by newer versions.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

mkdir build

%build
cd build
%cmake ../ \
	-DPYTHON_DESIRED:FILEPATH=%{__python3} \
	-DPYTHON_INSTALL_DIR:PATH=%{py3_sitescriptdir}

%{__make}
%{__make} doc-man

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_var}/cache/dnf

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

:> $RPM_BUILD_ROOT%{_var}/cache/dnf/packages.db

%if %{with yum_utils}
install -d $RPM_BUILD_ROOT%{_bindir}
for p in debuginfo-install needs-restarting find-repos-of-install repo-graph \
		package-cleanup repoclosure repodiff repomanage repoquery \
		reposync repotrack yum-builddep yum-config-manager yum-debug-dump \
		yum-debug-restore yum-groups-manager yumdownloader; do
	ln -sr $RPM_BUILD_ROOT%{_libexecdir}/dnf-utils $RPM_BUILD_ROOT%{_bindir}/$p
done
# These commands don't have a dedicated man page, so let's just point them
# to the utils page which contains their descriptions.
for m in find-repos-of-install.1 repoquery.1 repotrack.1; do
	echo ".so dnf-utils.1" > $RPM_BUILD_ROOT%{_mandir}/man1/$m
done
%{__mv} $RPM_BUILD_ROOT%{_libexecdir}/dnf-utils-3 $RPM_BUILD_ROOT%{_libexecdir}/dnf-utils

%else

for m in debuginfo-install needs-restarting repo-graph repoclosure repodiff \
		repomanage reposync yum-builddep yum-config-manager \
		yum-debug-dump yum-debug-restore yum-groups-manager \
		yumdownloader package-cleanup dnf-utils yum-utils; do
	%{__rm} $RPM_BUILD_ROOT%{_mandir}/man1/${m}.1*
done
%{__rm} $RPM_BUILD_ROOT%{_libexecdir}/dnf-utils-*
%endif

%if %{without yum_compatibility}
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man1/yum-changelog.1*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man5/yum-versionlock.5*
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man8/{yum-copr.8*,yum-versionlock.8*}
%endif

for d in $RPM_BUILD_ROOT%{py3_sitescriptdir}/{dnf-plugins,dnfpluginsextras}; do
%py3_comp $d
%py3_ocomp $d
done

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS README.rst
%config(noreplace) %{_sysconfdir}/dnf/plugins/copr.conf
%config(noreplace) %{_sysconfdir}/dnf/plugins/copr.d
%config(noreplace) %{_sysconfdir}/dnf/plugins/debuginfo-install.conf
%{py3_sitescriptdir}/dnf-plugins/builddep.py
%{py3_sitescriptdir}/dnf-plugins/changelog.py
%{py3_sitescriptdir}/dnf-plugins/config_manager.py
%{py3_sitescriptdir}/dnf-plugins/copr.py
%{py3_sitescriptdir}/dnf-plugins/debug.py
%{py3_sitescriptdir}/dnf-plugins/debuginfo-install.py
%{py3_sitescriptdir}/dnf-plugins/download.py
%{py3_sitescriptdir}/dnf-plugins/generate_completion_cache.py
%{py3_sitescriptdir}/dnf-plugins/groups_manager.py
%{py3_sitescriptdir}/dnf-plugins/needs_restarting.py
%{py3_sitescriptdir}/dnf-plugins/repoclosure.py
%{py3_sitescriptdir}/dnf-plugins/repodiff.py
%{py3_sitescriptdir}/dnf-plugins/repograph.py
%{py3_sitescriptdir}/dnf-plugins/repomanage.py
%{py3_sitescriptdir}/dnf-plugins/reposync.py
%{py3_sitescriptdir}/dnf-plugins/__pycache__/builddep.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/changelog.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/config_manager.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/copr.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/debug.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/debuginfo-install.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/download.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/generate_completion_cache.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/groups_manager.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/needs_restarting.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/repoclosure.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/repodiff.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/repograph.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/repomanage.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/reposync.*
%{py3_sitescriptdir}/dnfpluginscore/
%{_mandir}/man8/dnf-builddep.8*
%{_mandir}/man8/dnf-changelog.8*
%{_mandir}/man8/dnf-config-manager.8*
%{_mandir}/man8/dnf-copr.8*
%{_mandir}/man8/dnf-debug.8*
%{_mandir}/man8/dnf-debuginfo-install.8*
%{_mandir}/man8/dnf-download.8*
%{_mandir}/man8/dnf-generate_completion_cache.8*
%{_mandir}/man8/dnf-groups-manager.8*
%{_mandir}/man8/dnf-needs-restarting.8*
%{_mandir}/man8/dnf-repoclosure.8*
%{_mandir}/man8/dnf-repodiff.8*
%{_mandir}/man8/dnf-repograph.8*
%{_mandir}/man8/dnf-repomanage.8*
%{_mandir}/man8/dnf-reposync.8*
%if %{with yum_compatibility}
%{_mandir}/man1/yum-changelog.1*
%{_mandir}/man8/yum-copr.8*
%endif
%ghost %{_var}/cache/dnf/packages.db

%if %{with yum_utils}
%files -n dnf-utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/debuginfo-install
%attr(755,root,root) %{_bindir}/needs-restarting
%attr(755,root,root) %{_bindir}/find-repos-of-install
%attr(755,root,root) %{_bindir}/package-cleanup
%attr(755,root,root) %{_bindir}/repo-graph
%attr(755,root,root) %{_bindir}/repoclosure
%attr(755,root,root) %{_bindir}/repodiff
%attr(755,root,root) %{_bindir}/repomanage
%attr(755,root,root) %{_bindir}/repoquery
%attr(755,root,root) %{_bindir}/reposync
%attr(755,root,root) %{_bindir}/repotrack
%attr(755,root,root) %{_bindir}/yum-builddep
%attr(755,root,root) %{_bindir}/yum-config-manager
%attr(755,root,root) %{_bindir}/yum-debug-dump
%attr(755,root,root) %{_bindir}/yum-debug-restore
%attr(755,root,root) %{_bindir}/yum-groups-manager
%attr(755,root,root) %{_bindir}/yumdownloader
%attr(755,root,root) %{_libexecdir}/dnf-utils
%{_mandir}/man1/debuginfo-install.1*
%{_mandir}/man1/needs-restarting.1*
%{_mandir}/man1/repo-graph.1*
%{_mandir}/man1/repoclosure.1*
%{_mandir}/man1/repodiff.1*
%{_mandir}/man1/repomanage.1*
%{_mandir}/man1/reposync.1*
%{_mandir}/man1/yum-builddep.1*
%{_mandir}/man1/yum-config-manager.1*
%{_mandir}/man1/yum-debug-dump.1*
%{_mandir}/man1/yum-debug-restore.1*
%{_mandir}/man1/yum-groups-manager.1*
%{_mandir}/man1/yumdownloader.1*
%{_mandir}/man1/package-cleanup.1*
%{_mandir}/man1/dnf-utils.1*
%{_mandir}/man1/yum-utils.1*
%{_mandir}/man1/find-repos-of-install.1*
%{_mandir}/man1/repoquery.1*
%{_mandir}/man1/repotrack.1*
%endif

%files -n dnf-plugin-leaves
%defattr(644,root,root,755)
%{py3_sitescriptdir}/dnf-plugins/leaves.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/leaves.*
%{_mandir}/man8/dnf-leaves.8*

%files -n dnf-plugin-local
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/dnf/plugins/local.conf
%{py3_sitescriptdir}/dnf-plugins/local.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/local.*
%{_mandir}/man8/dnf-local.8*

%files -n dnf-plugin-migrate
%defattr(644,root,root,755)
%{py3_sitescriptdir}/dnf-plugins/migrate.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/migrate.*
%{_mandir}/man8/dnf-migrate.8*

%files -n dnf-plugin-post-transaction-actions
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/dnf/plugins/post-transaction-actions.conf
%config(noreplace) %{_sysconfdir}/dnf/plugins/post-transaction-actions.d
%{py3_sitescriptdir}/dnf-plugins/post-transaction-actions.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/post-transaction-actions.*
%{_mandir}/man8/dnf-post-transaction-actions.8*

%files -n dnf-plugin-show-leaves
%defattr(644,root,root,755)
%{py3_sitescriptdir}/dnf-plugins/show_leaves.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/show_leaves.*
%{_mandir}/man8/dnf-show-leaves.8*

%files -n dnf-plugin-versionlock
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/dnf/plugins/versionlock.conf
%config(noreplace) %{_sysconfdir}/dnf/plugins/versionlock.list
%{py3_sitescriptdir}/dnf-plugins/versionlock.*
%{py3_sitescriptdir}/dnf-plugins/__pycache__/versionlock.*
%{_mandir}/man8/dnf-versionlock.8*
%if %{with yum_compatibility}
%{_mandir}/man5/yum-versionlock.conf.5*
%{_mandir}/man8/yum-versionlock.8*
%endif
