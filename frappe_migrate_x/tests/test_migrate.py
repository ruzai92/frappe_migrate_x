import importlib
import os
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import cint

patches_loaded = False

"""bench --site <sitename> run-tests --module frappe_migrate_x.tests.test_migrate --test <test_case_name>"""
class TestMigrateX(FrappeTestCase):

    def test_init(self):
        print("hello world")

    def test_is_monkey_patches_folder_exist(self):
        my_app = ["frappe_migrate_x"]
        for app in frappe.get_installed_apps():
            if app in my_app:
                folder = frappe.get_app_path(app, "monkey_patches")
                print(folder)
                if os.path.exists(folder):
                    print("")
                    output = "monkey patches exists"
                    for module_name in os.listdir(folder):
                        if not module_name.endswith(".py") or module_name == "__init__.py":
                            continue

                        importlib.import_module(f"{app}.monkey_patches.{module_name[:-3]}")
            output = "does not exist."

        patches_loaded = True
                    
        self.assertTrue("monkey patches exists" in output)



    def test_is_app_exist_in_installed_apps(self):

        installed_apps = frappe.get_installed_apps()
        print(installed_apps)

        my_app = "frappe_migrate_x"
        for app in frappe.get_installed_apps():
            if app == my_app:
                print(app+"app exists")
                
        
        # print("app doesnt exists")