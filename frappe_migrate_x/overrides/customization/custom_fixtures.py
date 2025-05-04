# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os

import frappe
from frappe.core.doctype.data_import.data_import import export_json, import_doc
from frappe.utils.deprecations import deprecation_warning
import click
from frappe.utils.fixtures import import_fixtures, import_custom_scripts

def sync_fixtures(app=None):
	"""Import, overwrite fixtures from `[app]/fixtures`"""
	if app:
		click.secho(f"sync fixtures for {app}", fg="blue")
		frappe.flags.in_fixtures = True

		click.secho(f"import fixtures {app}", fg="blue")
		import_fixtures(app)
		click.secho(f"import custom scripts {app}", fg="blue")
		import_custom_scripts(app)

	frappe.flags.in_fixtures = False
