from importlib.metadata import version

from packaging.version import Version

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as create_frappe_custom_fields


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


def create_custom_fields():
    custom_fields = {
        "Journal Entry": [
            {
                "fieldname": "net_profit_sales_invoice",
                "label": "Sales Invoice",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "insert_after": "user_remark",
                "read_only": 1,
                "no_copy": 1,
            }
        ]
    }

    create_frappe_custom_fields(custom_fields, ignore_validate=True)
