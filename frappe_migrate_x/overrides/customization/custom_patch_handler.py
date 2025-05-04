# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
""" Patch Handler.

This file manages execution of manaully written patches. Patches are script
that apply changes in database schema or data to accomodate for changes in the
code.

Ways to specify patches:

1. patches.txt file specifies patches that run before doctype schema
migration. Each line represents one patch (old format).
2. patches.txt can alternatively also separate pre and post model sync
patches by using INI like file format:
	```patches.txt
	[pre_model_sync]
	app.module.patch1
	app.module.patch2


	[post_model_sync]
	app.module.patch3
	```

	When different sections are specified patches are executed in this order:
		1. Run pre_model_sync patches
		2. Reload/resync all doctype schema
		3. Run post_model_sync patches

	Hence any patch that just needs to modify data but doesn't depend on
	old schema should be added to post_model_sync section of file.

3. simple python commands can be added by starting line with `execute:`
`execute:` example: `execute:print("hello world")`
"""

import configparser
import time
from enum import Enum
from textwrap import dedent, indent

import frappe
from frappe.modules.patch_handler import run_single,get_patches_from_app

class PatchError(Exception):
	pass


class PatchType(Enum):
	pre_model_sync = "pre_model_sync"
	post_model_sync = "post_model_sync"


def run_all(skip_failing: bool = False, patch_type: PatchType | None = None, specific_app=None) -> None:
	"""run all pending patches"""
	executed = set(frappe.get_all("Patch Log", fields="patch", pluck="patch"))

	frappe.flags.final_patches = []

	def run_patch(patch):
		try:
			if not run_single(patchmodule=patch):
				print(patch + ": failed: STOPPED")
				raise PatchError(patch)
		except Exception:
			if not skip_failing:
				raise
			else:
				print("Failed to execute patch")

	patches = get_all_patches(patch_type=patch_type,specific_app=specific_app)

	for patch in patches:
		if patch and (patch not in executed):
			run_patch(patch)

	# patches to be run in the end
	for patch in frappe.flags.final_patches:
		patch = patch.replace("finally:", "")
		run_patch(patch)


def get_all_patches(patch_type: PatchType | None = None, specific_app = None) -> list[str]:

	if patch_type and not isinstance(patch_type, PatchType):
		frappe.throw(f"Unsupported patch type specified: {patch_type}")

	patches = []
	for app in frappe.get_installed_apps():
		if app == specific_app:
			patches.extend(get_patches_from_app(app, patch_type=patch_type))

	return patches