Name: nethserver-ns8-migration
Version: 1.0.13
Release: 1%{?dist}
Summary: NS7 to NS8 migration

License: GPLv3
URL: https://github.com/nethesis/icaro
Source: %{name}-%{version}.tar.gz
Source1: %{name}-cockpit.tar.gz

%global debug_package %{nil} 

BuildRequires: nethserver-devtools
Requires: wireguard-tools, kmod-wireguard
Requires: mariadb

%description
NS7 to NS8 migration

%prep
%setup -q


%build
%{makedocs}
perl createlinks
sed -i 's/_RELEASE_/%{version}/' %{name}.json

%install
rm -rf %{buildroot}
(cd root   ; find . -depth -print | cpio -dump %{buildroot})

mkdir -p %{buildroot}/usr/share/cockpit/%{name}/
mkdir -p %{buildroot}/usr/share/cockpit/nethserver/applications/
mkdir -p %{buildroot}/usr/libexec/nethserver/api/%{name}/
tar xvf %{SOURCE1} -C %{buildroot}/usr/share/cockpit/%{name}/
cp -a %{name}.json %{buildroot}/usr/share/cockpit/nethserver/applications/
cp -a api/* %{buildroot}/usr/libexec/nethserver/api/%{name}/

%{genfilelist} %{buildroot} --file /etc/sudoers.d/50_nsapi_nethserver_ns8_migration 'attr(0440,root,root)' > e-smith-%{version}-filelist


%files -f e-smith-%{version}-filelist
%defattr(-,root,root)
%dir %{_nseventsdir}/%{name}-update

%changelog
* Thu Jun 06 2024 Davide Principi <davide.principi@nethesis.it> - 1.0.13-1
- Account provider migration fails after NS8 reboot - Bug NethServer/dev#6942
- Migration tool duplicates Redis keys of node - Bug NethServer/dev#6940

* Thu May 30 2024 Davide Principi <davide.principi@nethesis.it> - 1.0.12-1
- Nextcloud login fails without displayName LDAP attribute - Bug NethServer/dev#6930

* Thu May 23 2024 Stefano Fancello <gentoo.stefano@gmail.com> - 1.0.11-1
- phonebook csv upload broken - nethesis/ns8-nethvoice#203

* Wed May 15 2024 Davide Principi <davide.principi@nethesis.it> - 1.0.10-1
- Mail version 1.4 - NethServer/dev#6895 

* Wed Mar 20 2024 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.9-1
- Mail migration fails with remote ldap account provider - Bug NethServer/dev#6883 
- Migration of roundcubemail is broken - Bug NethServer/dev#6876
- Migration tool workflow dead end - Bug NethServer/dev#6867
- Wrong validator for NethVoice in ns8-migration  - Bug NethServer/dev#6872

* Wed Feb 28 2024 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.8-1
- Roundcubemail and Webtop migration fixes - Bug NethServer/dev#6851

* Mon Feb 19 2024 Stefano Fancello <gentoo.stefano@gmail.com> - 1.0.7-1
- Add migration for SOGo - NethServer/dev#6804
- Add migration instructin for NethForge - NethServer/dev#6804
- Add migration for NethVoice - Nethesis/ns8-nethvoice#70
- Migrate phonebook password with NethVoice - Nethesis/ns8-nethvoice#116
- Cannot start NS8 migration with external account provider - Bug NethServer/dev#6795
- Wrong destination node selection in migration tool - Bug NethServer/dev#6792

* Wed Dec 13 2023 Davide Principi <davide.principi@nethesis.it> - 1.0.6-1
- Cannot start NS8 migration with external account provider - Bug NethServer/dev#6795
- Wrong destination node selection in migration tool - Bug NethServer/dev#6792

* Fri Dec 01 2023 Davide Principi <davide.principi@nethesis.it> - 1.0.5-1
- Migration of Samba fails without file server - Bug NethServer/dev#6785
- Sticky error connecting to NS8 in migration tool - Bug NethServer/dev#6783
- Migration tool wg0 interface name conflict - Bug NethServer/dev#6782
- Migrate Getmail configuration to NS8 - NethServer/dev#6776

* Fri Nov 10 2023 Davide Principi <davide.principi@nethesis.it> - 1.0.4-1
- Fix File Server migration
- Add Transifex configuration

* Thu Nov 09 2023 Davide Principi <davide.principi@nethesis.it> - 1.0.3-1
- Pipe character in nethserver-ns8-migration corrupts config DB - Bug NethServer/dev#6769

* Tue May 30 2023 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.2-1
- rsync on ns7 does not expand wildcard of --chown nethserver-ns8-migration/pull/41

* Wed May 10 2023 Davide Principi <davide.principi@nethesis.it> - 1.0.1-1
- Migrate home dirs to Samba "homes" volume -- NethServer/dev#6747

* Fri Apr 28 2023 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.0-1
- First public release for NS8 Beta 1

