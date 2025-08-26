Name: nethserver-ns8-migration
Version: 1.3.4
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
* Tue Aug 26 2025 Davide Principi <davide.principi@nethesis.it> - 1.3.4-1
- OpenLDAP migration trims accented chars - NethServer/dev#7576
- WebTop 1.5 with Tomcat and Postgresql Version Upgrade [always migrate to WebTop 1.4.4] - NethServer/dev#7489

* Mon Jun 30 2025 Stefano Fancello <gentoo.stefano@gmail.com> - 1.3.3-1
- fix(nethvoice): Don't fail if /etc/fias.conf doesn't exist (#121)

* Mon Jun 23 2025 Davide Principi <davide.principi@nethesis.it> - 1.3.2-1
- Migration to orphan single node cluster fails - NethServer/dev#7508
- NethHotel: port old NethHotel from NethVoice14 - NethServer/dev#7425

* Tue May 20 2025 Davide Principi <davide.principi@nethesis.it> - 1.3.1-1
- Migration tool app abort error with non-root user - NethServer/dev#7449
- Migration Mail start fails with HTTP 500 error - NethServer/dev#7464

* Mon May 05 2025 Davide Principi <davide.principi@nethesis.it> - 1.3.0-1
- Compatibility check in add-node - NethServer/dev#7376
- Task progress lost and timeout during migration - NethServer/dev#7319

* Fri Apr 04 2025 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.2.1-1
- Webtop migration to NS8 and failure to access mailboxes in some cases - NethServer/dev#7371

* Wed Jan 22 2025 Davide Principi <davide.principi@nethesis.it> - 1.2.0-1
- Migration: prevent app migration to nodes with allocated ports - NethServer/dev#7226
- NS7 join fails if user domain directory.nh exists - NethServer/dev#7222
- Browser page refresh leads to Start migration button again - NethServer/dev#7239
- Nethvoice: install nethvoice proxy as a migration dependency - NethServer/dev#7221

* Thu Dec 12 2024 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.1.0-1
- Migration tool blindly removes external user domain - NethServer/dev#7199
- NS6 (7) OpenLDAP migration failed - NethServer/dev#7101
- Rename of directory.nh for multiple migrations - NethServer/dev#7103
- Updates suspended after failed NS7 migration attempt - NethServer/dev#7192

* Wed Nov 13 2024 Davide Principi <davide.principi@nethesis.it> - 1.0.18-1
- Joining multiple NS7 systems with the same account provider to NS8 fails - Bug NethServer/dev#7111
- Webtop NS8 migration validation error - Bug NethServer/dev#7085

* Tue Oct 08 2024 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.17-1
- Migration: Unable to complete with disabled applications - Bug NethServer/dev#7037
- Webtop Pecbridge component - NethServer/dev#6984

* Thu Sep 12 2024 Stephane de Labrusse <stephdl@de-labrusse.fr> - 1.0.16-1
- mattermost: migration cannot be finished - Bug NethServer/dev#7005
- Create admin account for NS7 migration - NethServer/dev#6994

* Fri Aug 02 2024 Davide Principi <davide.principi@nethesis.it> - 1.0.15-1
- Migration of Nextcloud 27.1.11 - NethServer/dev#6964
- A failed connection to OpenLDAP breaks the migration - Bug NethServer/dev#6985

* Mon Jul 15 2024 Stefano Fancello <gentoo.stefano@gmail.com> - 1.0.14-1
- NethVoice: add nethcti customer card volume - nethesis/ns8-nethvoice#263

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

