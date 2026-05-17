from inspect import signature

from erpnext.accounts.doctype.sales_invoice.sales_invoice_dashboard import (
	get_data as get_sales_invoice_dashboard_data,
)


def get_data(data=None):
	dashboard_data = get_original_dashboard_data(data)

	dashboard_data.setdefault("non_standard_fieldnames", {})
	dashboard_data["non_standard_fieldnames"]["Indirct Cost"] = "sales_invoice"
	dashboard_data["non_standard_fieldnames"]["Journal Entry"] = "net_profit_sales_invoice"

	add_indirct_cost_connection(dashboard_data)

	return dashboard_data


def get_original_dashboard_data(data=None):
	if signature(get_sales_invoice_dashboard_data).parameters:
		return get_sales_invoice_dashboard_data(data)

	return get_sales_invoice_dashboard_data()


def add_indirct_cost_connection(dashboard_data):
	for transaction_group in dashboard_data.get("transactions", []):
		if transaction_group.get("label") == "Payment":
			add_item(transaction_group, "Indirct Cost")
			return

	dashboard_data.setdefault("transactions", []).append(
		{
			"label": "Payment",
			"items": ["Indirct Cost"],
		}
	)


def add_item(transaction_group, item):
	items = transaction_group.setdefault("items", [])
	if item not in items:
		items.append(item)
