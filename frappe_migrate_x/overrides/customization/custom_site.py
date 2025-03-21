# imports - standard imports
import os
import shutil
import sys

# imports - third party imports
import click
# imports - module imports
import frappe
from frappe.commands import get_site, pass_context
from frappe.exceptions import SiteNotSpecifiedError

@click.command("migrate")
@click.option("--skip-failing", is_flag=True, help="Skip patches that fail to run")
@click.option("--skip-search-index", is_flag=True, help="Skip search indexing for web documents")
@click.option("--specific-app", help="Migrate for specific application")
@pass_context
def migrate(context, skip_failing=False, skip_search_index=False, specific_app=None):
	"Run patches, sync schema and rebuild files/translations"
	from traceback_with_variables import activate_by_import

	from frappe_migrate_x.overrides.customization.custom_migrate import SiteMigration

	for site in context.sites:
		click.secho(f"Migrating {site}", fg="green")
		try:
			SiteMigration(
				skip_failing=skip_failing,
				skip_search_index=skip_search_index,
				specific_app=specific_app
			).run(site=site)
		finally:
			print()
	if not context.sites:
		raise SiteNotSpecifiedError
