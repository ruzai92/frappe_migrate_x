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
        # for app in frappe.get_installed_apps():
        #     if app == my_app:
        #         print(app+"app exists")
                    
        # # print("app doesnt exists")

        if my_app not in installed_apps:
            print(f"{my_app} doenst exist")
        else:
            print(f"{my_app} do exist")

    def test_run_all(self):
        # executed = set(frappe.get_all("Patch Log", fields="patch", pluck="patch"))
        # print(executed)
        app = "frappe_migrate_x"
        patches_txt = frappe.get_pymodule_path(app, "patches.txt")
        print(patches_txt)

    def test_get_all_patches(self):
        pre_model_sync = "pre_model_sync"
        post_model_sync = "post_model_sync"
        
        # PatchType.pre_model_sync
        # PatchType.post_model_sync

        patch_type = pre_model_sync
        patches = []
        for app in frappe.get_installed_apps():
            patches.extend(get_patches_from_app(app, patch_type=patch_type))


    def test_get_default_apps(self):

        default_apps = ["frappe", "erpnext"]
        specific_app = "umserp_purchasing"

        for default in default_apps:
            if default in frappe.get_installed_apps():
                print(default+" is exist")

        if specific_app in frappe.get_installed_apps():
            print(f"{specific_app} do exist")
            