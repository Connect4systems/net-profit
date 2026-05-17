from importlib.metadata import version

from packaging.version import Version

import frappe


def before_install():
    validate_major_version("frappe", "15")
    validate_major_version("erpnext", "15")

    installed_apps = frappe.get_installed_apps()
    if "erpnext" not in installed_apps:
        frappe.throw("Please install ERPNext on this site before installing Net Profit.")


def validate_major_version(package_name, expected_major):
    package_version = Version(version(package_name))
    if str(package_version.major) != expected_major:
        frappe.throw(
            f"Net Profit requires {package_name} v{expected_major}. "
            f"Found {package_name} {package_version}."
        )
