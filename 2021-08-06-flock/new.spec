Name:           python-pello
Version:        1.0.2
Release:        1%{?dist}
Summary:        Example Python library

License:        MIT
URL:            https://github.com/fedora-python/Pello
Source0:        %{url}/archive/v%{version}/Pello-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

# Build dependencies: generated from upstream metadata (%generate_buildrequires, later)

# Test dependencies: generated from upstream metadata (%generate_buildrequires, later)

# Runtime dependencies: used as build-time (with the proper flag to %generate_buildrequires)

%global _description %{expand:
A python module which provides a convenient example.
This description provides some details.}

%description %_description

%package -n python3-pello
Summary:        %{summary}
Recommends:     python3-pello+color

%description -n python3-pello %_description


%pyproject_extras_subpkg -n python3-pello color


%prep
%autosetup -p1 -n Pello-%{version}


%generate_buildrequires
# The build/test/runtime BuildRequires are generated from upstream metadata.
# Read the docs for this macro!
%pyproject_buildrequires -t


%build
# The macro supports setup.py-based and pyproject.toml-based build
%pyproject_wheel


%install
# The macro supports setup.py-based and pyproject.toml-based build
%pyproject_install

# Library and metadata files can be saved for use in %%files
%pyproject_save_files pello


%check
# If upstream uses tox, this will run it in Fedora's environment:
%tox
# Otherwise you can use %%pytest, or a script, or %%py3_check_import


# For %%{pyproject_files} handles code files (see %%pyproject_save_files), but
# executables, documentation and license must be listed in the spec file:
%files -n python3-pello -f %{pyproject_files}
%doc README.md
%license LICENSE.txt
%{_bindir}/pello_greeting


