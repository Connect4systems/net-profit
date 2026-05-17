app_name = "net_profit"
app_title = "Net Profit"
app_publisher = "Net Profit"
app_description = "Net Profit app for Frappe and ERPNext"
app_email = "admin@example.com"
app_license = "MIT"

required_apps = ["erpnext"]

# Includes in <head>
# app_include_css = "/assets/net_profit/css/net_profit.css"
# app_include_js = "/assets/net_profit/js/net_profit.js"

doctype_js = {
	"Sales Invoice": "public/js/sales_invoice.js",
}

# Installation
before_install = "net_profit.install.before_install"
after_install = "net_profit.install.create_custom_fields"
after_migrate = "net_profit.install.create_custom_fields"
