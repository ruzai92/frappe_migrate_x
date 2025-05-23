# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import contextlib
import functools
import json
import os
from textwrap import dedent

import frappe
import frappe.model.sync
# import frappe.modules.patch_handler
import frappe_migrate_x.overrides.customization.custom_patch_handler
import frappe.translate
from frappe.cache_manager import clear_global_cache
from frappe.core.doctype.language.language import sync_languages
from frappe.core.doctype.scheduled_job_type.scheduled_job_type import sync_jobs
from frappe.database.schema import add_column
from frappe.deferred_insert import save_to_db as flush_deferred_inserts
from frappe.desk.notifications import clear_notifications
# from frappe.modules.patch_handler import PatchType
from  frappe_migrate_x.overrides.customization.custom_patch_handler import PatchType
from frappe.modules.utils import sync_customizations
from frappe.search.website_search import build_index_for_all_routes
from frappe.utils.connections import check_connection
from frappe.utils.dashboard import sync_dashboards
# from frappe.utils.fixtures import sync_fixtures
from frappe_migrate_x.overrides.customization.custom_fixtures import sync_fixtures
from frappe.website.utils import clear_website_cache
import frappe_migrate_x.overrides.customization.custom_sync
import click
from frappe.migrate import SiteMigration

BENCH_START_MESSAGE = dedent(
	"""
	Cannot run bench migrate without the services running.
	If you are running bench in development mode, make sure that bench is running:

	$ bench start

	Otherwise, check the server logs and ensure that all the required services are running.
	"""
)


def atomic(method):
	@functools.wraps(method)
	def wrapper(*args, **kwargs):
		try:
			ret = method(*args, **kwargs)
			frappe.db.commit()
			return ret
		except Exception as e:
			# database itself can be gone while attempting rollback.
			# We should preserve original exception in this case.
			with contextlib.suppress(Exception):
				frappe.db.rollback()
			raise e

	return wrapper


class SiteMigrationX(SiteMigration):
	"""Migrate all apps to the current version, will:
	- run before migrate hooks
	- run patches
	- sync doctypes (schema)
	- sync dashboards
	- sync jobs
	- sync fixtures
	- sync customizations
	- sync languages
	- sync web pages (from /www)
	- run after migrate hooks
	"""

	def __init__(self, skip_failing: bool = False, skip_search_index: bool = False, 
			  specific_app:str = None, skip_fixtures: bool = False) -> None:
		self.skip_failing = skip_failing
		self.skip_search_index = skip_search_index
		self.specific_app = specific_app
		self.skip_fixtures = skip_fixtures
		self.default_apps = ["frappe", "erpnext"]
		self.default_apps.append(self.specific_app)

	@atomic
	def pre_schema_updates(self):
		"""Executes `before_migrate` hooks"""
		if len(self.default_apps) > 0:
			for app in frappe.get_installed_apps():
				if app in self.default_apps:
					for fn in frappe.get_hooks("before_migrate", app_name=app):
						frappe.get_attr(fn)()


	@atomic
	def run_schema_updates(self):
		"""Run patches as defined in patches.txt, sync schema changes as defined in the {doctype}.json files"""
		if len(self.default_apps) > 0:
			for app in frappe.get_installed_apps():
				if app in self.default_apps:
					frappe_migrate_x.overrides.customization.custom_patch_handler.run_all(
						skip_failing=self.skip_failing, patch_type=PatchType.pre_model_sync,specific_app=app
					)
					frappe_migrate_x.overrides.customization.custom_sync.sync_all(specific_app=app)
					frappe_migrate_x.overrides.customization.custom_patch_handler.run_all(
						skip_failing=self.skip_failing, patch_type=PatchType.post_model_sync,specific_app=app
					)

			click.secho(f"finish run_schema_updates", fg="yellow")

	@atomic
	def post_schema_updates(self):
		"""Execute pending migration tasks post patches execution & schema sync
		This includes:
		* Sync `Scheduled Job Type` and scheduler events defined in hooks
		* Sync fixtures & custom scripts
		* Sync in-Desk Module Dashboards
		* Sync customizations: Custom Fields, Property Setters, Custom Permissions
		* Sync Frappe's internal language master
		* Flush deferred inserts made during maintenance mode.
		* Sync Portal Menu Items
		* Sync Installed Applications Version History
		* Execute `after_migrate` hooks
		"""
		click.secho(f"sync jobs", fg="blue")
		sync_jobs()

		if len(self.default_apps) > 0:
			for app in frappe.get_installed_apps():
				if app in self.default_apps:
					if not self.skip_fixtures:
						click.secho(f"sync {app} fixtures", fg="blue")
						sync_fixtures(app)

					click.secho(f"sync {app} dashboards", fg="blue")
					sync_dashboards(app)
					click.secho(f"sync {app} customizations ", fg="blue")
					sync_customizations(app)

		click.secho(f"sync languages", fg="blue")
		sync_languages()		
		flush_deferred_inserts()

		frappe.get_single("Portal Settings").sync_menu()
		frappe.get_single("Installed Applications").update_versions()


		if len(self.default_apps) > 0:
			for app in frappe.get_installed_apps():
				if app in self.default_apps:
					for fn in frappe.get_hooks("after_migrate", app_name=app):
						click.secho(f"{fn}", fg="red")
						frappe.get_attr(fn)()

	def run(self, site: str):
		"""Run Migrate operation on site specified. This method initializes
		and destroys connections to the site database.
		"""
		
		if site:
			frappe.init(site=site)
			frappe.connect()

		if not self.required_services_running():
			raise SystemExit(1)

		self.setUp()
		try:
			self.pre_schema_updates()
			self.run_schema_updates()
			self.post_schema_updates()
		finally:
			self.tearDown()
			frappe.destroy()
