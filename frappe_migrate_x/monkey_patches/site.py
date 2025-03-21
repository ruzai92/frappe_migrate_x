from frappe.commands import site as s
from frappe_migrate_x.overrides.customization.custom_site import migrate

s.migrate = migrate