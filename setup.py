from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_migrate_x/__init__.py
from frappe_migrate_x import __version__ as version

setup(
	name="frappe_migrate_x",
	version=version,
	description="Frappe custom bench migrate for specfic app.",
	author="ruzai92",
	author_email="ahmad.ruzaini@ums.edu.my",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
