Name:           check_ib_switch
Version:        0.0.4
%global gittag 0.0.4
Release:        1%{?dist}
Summary:        Nagios script to check the status and fault in unmanaged Mellanox Infiniband switches

License:        Apache License 2.0
URL:            https://github.com/guilbaults/%{name}
Source0:        https://github.com/guilbaults/%{name}/archive/v%{gittag}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python%{python3_pkgversion}-devel
Requires:       mft
Requires:       python3

%description
This tool is used to monitor unmanaged Infiniband switches made by Mellanox

%prep
%autosetup -n %{name}-%{gittag}
%setup -q

%build

%install
mkdir -p %{buildroot}/usr/lib64/nagios/plugins/

sed -i -e '1i#!/usr/bin/env python3' %{name}.py
install -m 0755 %{name}.py %{buildroot}/usr/lib64/nagios/plugins/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
/usr/lib64/nagios/plugins/%{name}

%changelog
* Tue May 19 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.4-1
- Increasing fan speed threshold
* Wed May 13 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.3-1
- Fix format() manual/automatic numbering
* Wed May 13 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.2-1
- Updating fan speed threshold
* Thu May 7 2020 Simon Guilbault <simon.guilbault@calculquebec.ca> 0.0.1-1
- Initial release

