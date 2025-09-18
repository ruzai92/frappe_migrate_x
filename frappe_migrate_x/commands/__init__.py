from __future__ import unicode_literals, absolute_import, print_function
import click
import frappe
from frappe.commands import pass_context, get_site
from frappe_migrate_x.overrides.customization.custom_migrate import SiteMigrationX
from frappe.exceptions import SiteNotSpecifiedError

def get_available_apps(site):
    """Get list of installed apps for a site"""
    frappe.init(site=site)
    return frappe.get_installed_apps()

def interactive_app_selection(site):
    """Interactive app selection using checkboxes"""
    available_apps = get_available_apps(site)
    
    if not available_apps:
        click.secho("No apps found for this site", fg="red")
        return []
    
    click.secho(f"\nAvailable apps for site '{site}':", fg="cyan")
    click.secho("Use spacebar to select/deselect, Enter to confirm selection\n", fg="yellow")
    
    selected_apps = []
    
    while True:
        for i, app in enumerate(available_apps):
            status = "[x]" if app in selected_apps else "[ ]"
            color = "green" if app in selected_apps else "white"
            click.secho(f"{i+1}. {status} {app}", fg=color)
        
        click.secho(f"\nCurrently selected: {len(selected_apps)} apps", fg="cyan")
        if selected_apps:
            click.secho(f"Selected apps: {', '.join(selected_apps)}", fg="green")
        
        click.secho("\nCommands:", fg="yellow")
        click.secho("Enter app number to toggle selection, 'a' for all, 'n' for none, 'c' to confirm", fg="yellow")
        
        choice = click.prompt("Your choice").strip().lower()
        
        if choice == 'c':
            if selected_apps:
                return selected_apps
            else:
                click.secho("Please select at least one app", fg="red")
                continue
        elif choice == 'a':
            selected_apps = available_apps.copy()
        elif choice == 'n':
            selected_apps = []
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(available_apps):
                app = available_apps[index]
                if app in selected_apps:
                    selected_apps.remove(app)
                else:
                    selected_apps.append(app)
            else:
                click.secho("Invalid app number", fg="red")
        else:
            click.secho("Invalid choice", fg="red")
        
        click.clear()

@click.command('migrate-x')
@click.option("--skip-failing", is_flag=True, help="Skip patches that fail to run")
@click.option("--skip-search-index", is_flag=True, help="Skip search indexing for web documents")
@click.option("--app", help="Migrate for specific application (use --app myapp or --multi-app for multiple apps)")
@click.option("--multi-app", is_flag=True, help="Interactive multiple app selection mode")
@click.option("--skip-fixtures", is_flag=True, help="Skip sync fixtures during migration")
@pass_context
def migrate_x(context, skip_failing=False, skip_search_index=False, app=None, multi_app=False, skip_fixtures=False):
    """Migrate apps with enhanced options.
    
    This single command handles all migration scenarios:
    - Single app: --app myapp
    - Multiple apps: --multi-app  
    - Skip fixtures: --skip-fixtures (works with both modes)
    - Skip failing patches: --skip-failing
    - Skip search indexing: --skip-search-index
    
    Examples:
    bench --site mysite migrate-x --app erpnext --skip-fixtures
    bench --site mysite migrate-x --multi-app --skip-fixtures --skip-failing
    """

    if not context.sites:
        raise SiteNotSpecifiedError
    
    selected_apps = []
    
    if multi_app:
        if len(context.sites) > 1:
            click.secho("Multi-app mode works with single site only. Please specify one site.", fg="red")
            return
            
        site = context.sites[0]
        selected_apps = interactive_app_selection(site)
        
        if not selected_apps:
            click.secho("No apps selected. Exiting.", fg="yellow")
            return
            
    elif app:
        selected_apps = [app]
    else:
        click.secho("Please provide specific app to migrate using --app or use --multi-app mode", fg="red")
        return
    
    confirm = click.confirm("Are you sure you want to continue?")
    if not confirm:
        return
    
    click.secho(f"Initializing migration for apps: {', '.join(selected_apps)}", fg="yellow")
    
    for site in context.sites:
        click.secho(f"Current site: {site}", fg="yellow")
        frappe.init(site=site)
        
        installed_apps = frappe.get_installed_apps()
        
        for selected_app in selected_apps:
            if selected_app not in installed_apps:
                click.secho(f"{selected_app} is not installed on site {site}", fg="red")
                return
        
        try:
            SiteMigrationX(
                skip_failing=skip_failing,
                skip_search_index=skip_search_index,
                specific_apps=selected_apps,
                skip_fixtures=skip_fixtures
            ).run(site=site)
        finally:
            print()
	

commands = [
    migrate_x
]