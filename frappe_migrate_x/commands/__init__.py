from __future__ import unicode_literals, absolute_import, print_function
import click
import frappe
from frappe.commands import pass_context, get_site
from frappe_migrate_x.overrides.customization.custom_migrate import SiteMigrationX
from frappe.exceptions import SiteNotSpecifiedError
# from frappe import get_installed_apps

@click.command('migrate-x')
@click.option("--skip-failing", is_flag=True, help="Skip patches that fail to run")
@click.option("--skip-search-index", is_flag=True, help="Skip search indexing for web documents")
@click.option("--app", help="Migrate for specific application")
@click.option("--skip-fixtures", is_flag=True, help="Skip sync fixtures")
@pass_context
def migrate_x(context, skip_failing=False, skip_search_index=False, app=None, skip_fixtures=False):
    "Migrate specific app only, enable to skip sync fixtures"

    confirm = click.confirm("Are you sure you want to continue?")
    if not confirm:
        return
    
    if app:
        click.secho(f"Initializing.....", fg="yellow")
        for site in context.sites:
            click.secho(f"Current site:{site}", fg="yellow")
            frappe.init(site=site)

            if app not in frappe.get_installed_apps():
                click.secho(f"{app} is not installed....", fg="red")
                return
            
            try:
                SiteMigrationX(
                    skip_failing=skip_failing,
                    skip_search_index=skip_search_index,
                    specific_app=app,
                    skip_fixtures=skip_fixtures
                ).run(site=site)
            finally:
                print()
        if not context.sites:
            raise SiteNotSpecifiedError
    else:
        click.secho(f"Please provide specific app to migrate", fg="red")
	

commands = [
    migrate_x
]