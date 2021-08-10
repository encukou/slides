Name:           python-pello
Version:        1.0.2
Release:        1%{?dist}
Summary:        Example Python library

License:        MIT
URL:            https://github.com/fedora-python/Pello
Source0:        %{url}/archive/v%{version}/Pello-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

# Build dependencies: specified manually!!
BuildRequires:  python3-setuptools

# Test dependencies: specified manually!!
BuildRequires:  python3-pytest >= 3

# Runtime dependencies: needed to be specified manually on build time to run tests
BuildRequires:  python3-blessings

%global _description %{expand:
A python module which provides a convenient example.
This description provides some details.}

%description %_description

%package -n python3-pello
Summary:        %{summary}
Recommends:     python3-pello+color

%description -n python3-pello %_description

# The metadata directory needed to be specified manually for Python extras
%python_extras_subpkg -n python3-pello color -i %{python3_sitelib}/*.egg-info


%prep
%autosetup -p1 -n Pello-%{version}


%build
# The macro only supported projects with setup.py
%py3_build


%install
# The macro only supported projects with setup.py
%py3_install


%check
# The old guidelines mentioned one way of running tests which is deprecated
# (in setuptools upstream) and in many cases leads to unexpected results.
# (But alternatively, new test macros can be used here as well)
%{python3} setup.py test


%files -n python3-pello
%doc README.md
%license LICENSE.txt
%{_bindir}/pello_greeting

# The library files needed to be listed manually,
# often with extra care about the .pyc cache (although not in this example)
%{python3_sitelib}/pello/

# The metadata files needed to be listed manually
%{python3_sitelib}/Pello-*.egg-info/

