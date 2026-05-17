import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	report_summary = get_report_summary(data)
	chart = get_chart(data)

	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"label": _("Sales Invoice"),
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 160,
		},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
		{"label": _("Net Sales"), "fieldname": "net_sales", "fieldtype": "Currency", "width": 130},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 130},
		{"label": _("Indirect Cost"), "fieldname": "indirect_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Net Profit"), "fieldname": "net_profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Profit %"), "fieldname": "profit_percent", "fieldtype": "Percent", "width": 100},
		{
			"label": _("Indirect Cost Count"),
			"fieldname": "indirect_cost_count",
			"fieldtype": "Int",
			"width": 140,
		},
	]


def get_data(filters):
	conditions = ["si.docstatus = 1"]
	values = {}

	if filters.company:
		conditions.append("si.company = %(company)s")
		values["company"] = filters.company

	if filters.from_date:
		conditions.append("si.posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.to_date:
		conditions.append("si.posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	if filters.customer:
		conditions.append("si.customer = %(customer)s")
		values["customer"] = filters.customer

	if filters.sales_invoice:
		conditions.append("si.name = %(sales_invoice)s")
		values["sales_invoice"] = filters.sales_invoice

	return frappe.db.sql(
		f"""
		SELECT
			si.name AS sales_invoice,
			si.posting_date,
			si.customer,
			si.customer_name,
			si.base_net_total AS net_sales,
			si.base_grand_total AS grand_total,
			IFNULL(indirect_cost.amount, 0) AS indirect_cost,
			(si.base_net_total - IFNULL(indirect_cost.amount, 0)) AS net_profit,
			CASE
				WHEN si.base_net_total = 0 THEN 0
				ELSE ((si.base_net_total - IFNULL(indirect_cost.amount, 0)) / si.base_net_total) * 100
			END AS profit_percent,
			IFNULL(indirect_cost.cost_count, 0) AS indirect_cost_count
		FROM `tabSales Invoice` si
		LEFT JOIN (
			SELECT
				ic.sales_invoice,
				SUM(ict.amount) AS amount,
				COUNT(DISTINCT ic.name) AS cost_count
			FROM `tabIndirct Cost` ic
			INNER JOIN `tabindirect cost table` ict
				ON ict.parent = ic.name
				AND ict.parenttype = 'Indirct Cost'
				AND ict.parentfield = 'expinses'
			WHERE ic.docstatus = 1
				AND IFNULL(ic.sales_invoice, '') != ''
			GROUP BY ic.sales_invoice
		) indirect_cost
			ON indirect_cost.sales_invoice = si.name
		WHERE {" AND ".join(conditions)}
		ORDER BY si.posting_date DESC, si.name DESC
		""",
		values,
		as_dict=True,
	)


def get_report_summary(data):
	net_sales = sum(flt(row.net_sales) for row in data)
	grand_total = sum(flt(row.grand_total) for row in data)
	indirect_cost = sum(flt(row.indirect_cost) for row in data)
	net_profit = sum(flt(row.net_profit) for row in data)
	profit_percent = (net_profit / net_sales * 100) if net_sales else 0

	return [
		{"value": net_sales, "label": _("Net Sales"), "datatype": "Currency"},
		{"value": grand_total, "label": _("Grand Total"), "datatype": "Currency"},
		{"value": indirect_cost, "label": _("Indirect Cost"), "datatype": "Currency"},
		{"value": net_profit, "label": _("Net Profit"), "datatype": "Currency"},
		{"value": profit_percent, "label": _("Profit %"), "datatype": "Percent"},
	]


def get_chart(data):
	return {
		"data": {
			"labels": [_("Net Sales"), _("Indirect Cost"), _("Net Profit")],
			"datasets": [
				{
					"name": _("Amount"),
					"values": [
						sum(flt(row.net_sales) for row in data),
						sum(flt(row.indirect_cost) for row in data),
						sum(flt(row.net_profit) for row in data),
					],
				}
			],
		},
		"type": "bar",
	}
