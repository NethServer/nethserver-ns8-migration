Name: nethserver-ns8-migration
Version: 1.0.0
Release: 1%{?dist}
Summary: NS7 to NS8 migration

License: GPLv3
URL: https://github.com/nethesis/icaro
Source: %{name}-%{version}.tar.gz
Source1: %{name}-cockpit.tar.gz

%global debug_package %{nil} 
Source2: agent

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
install -D -m 0755 %{SOURCE2} %{buildroot}/%{_bindir}/agent

%{genfilelist} %{buildroot} --file /etc/sudoers.d/50_nsapi_nethserver_ns8_migration 'attr(0440,root,root)' > e-smith-%{version}-filelist


%files -f e-smith-%{version}-filelist
%defattr(-,root,root)
%dir %{_nseventsdir}/%{name}-update

%changelog
* Fri Apr 28 2023 Giacomo Sanchietti <giacomo.sanchietti@nethesis.it> - 1.0.0-1
- First public release for NS8 Beta 1

