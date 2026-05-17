import frappe
from frappe import _
from frappe.utils import cint, flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	gross_profit_result = get_gross_profit_result(filters)
	columns = get_columns(gross_profit_result[0])
	data = get_data(gross_profit_result[1])
	report_summary = get_report_summary(data)
	chart = get_chart(data)

	return columns, data, None, chart, report_summary


def get_gross_profit_result(filters):
	from erpnext.accounts.report.gross_profit.gross_profit import execute as gross_profit_execute

	gross_profit_filters = frappe._dict(filters)
	gross_profit_filters.based_on = gross_profit_filters.get("based_on") or "Invoice"

	return gross_profit_execute(gross_profit_filters)


def get_columns(gross_profit_columns):
	columns = list(gross_profit_columns)
	existing_fieldnames = {get_column_fieldname(column) for column in columns}

	for column in get_net_profit_columns():
		if column["fieldname"] not in existing_fieldnames:
			columns.append(column)

	return columns


def get_column_fieldname(column):
	if isinstance(column, dict):
		return column.get("fieldname")

	return None


def get_net_profit_columns():
	return [
		{"label": _("Direct Cost"), "fieldname": "direct_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Indirect Cost"), "fieldname": "indirect_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Net Profit"), "fieldname": "net_profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Net Profit %"), "fieldname": "net_profit_percent", "fieldtype": "Percent", "width": 120},
	]


def get_data(gross_profit_data):
	data = [frappe._dict(row) for row in gross_profit_data]
	indirect_cost_map = get_indirect_cost_map(get_sales_invoices(data))
	invoice_sales_map = get_invoice_sales_map(data)

	current_invoice = None
	for row in data:
		invoice = get_row_sales_invoice(row, current_invoice)
		if is_invoice_row(row, invoice):
			current_invoice = invoice

		row.direct_cost = get_direct_cost(row)
		row.indirect_cost = get_row_indirect_cost(row, invoice, indirect_cost_map, invoice_sales_map)
		row.net_profit = flt(row.get("gross_profit")) - flt(row.indirect_cost)
		row.net_profit_percent = (row.net_profit / get_sales_amount(row) * 100) if get_sales_amount(row) else 0

	return data


def get_sales_invoices(data):
	invoices = set()
	current_invoice = None

	for row in data:
		invoice = get_row_sales_invoice(row, current_invoice)
		if is_invoice_row(row, invoice):
			current_invoice = invoice
			invoices.add(invoice)
		elif invoice:
			invoices.add(invoice)

	return list(invoices)


def get_row_sales_invoice(row, current_invoice=None):
	if row.get("sales_invoice"):
		return row.sales_invoice

	invoice_or_item = row.get("invoice_or_item")
	if invoice_or_item and frappe.db.exists("Sales Invoice", invoice_or_item):
		return invoice_or_item

	return current_invoice


def is_invoice_row(row, invoice):
	return bool(invoice and row.get("invoice_or_item") == invoice and not cint(row.get("indent")))


def get_indirect_cost_map(sales_invoices):
	if not sales_invoices:
		return {}

	amounts = frappe.db.sql(
		"""
		SELECT
			ic.sales_invoice,
			SUM(ict.amount) AS amount
		FROM `tabIndirct Cost` ic
		INNER JOIN `tabindirect cost table` ict
			ON ict.parent = ic.name
			AND ict.parenttype = 'Indirct Cost'
			AND ict.parentfield = 'expinses'
		WHERE ic.docstatus = 1
			AND ic.sales_invoice IN %(sales_invoices)s
		GROUP BY ic.sales_invoice
		""",
		{"sales_invoices": tuple(sales_invoices)},
		as_dict=True,
	)

	return {row.sales_invoice: flt(row.amount) for row in amounts}


def get_invoice_sales_map(data):
	sales_map = {}
	current_invoice = None

	for row in data:
		invoice = get_row_sales_invoice(row, current_invoice)
		if is_invoice_row(row, invoice):
			current_invoice = invoice
			continue

		if invoice:
			sales_map[invoice] = sales_map.get(invoice, 0) + get_sales_amount(row)

	return sales_map


def get_direct_cost(row):
	if row.get("buying_amount") is not None:
		return flt(row.buying_amount)

	return get_sales_amount(row) - flt(row.get("gross_profit"))


def get_sales_amount(row):
	for fieldname in ("base_amount", "selling_amount", "amount", "net_sales"):
		if row.get(fieldname) is not None:
			return flt(row.get(fieldname))

	return 0


def get_row_indirect_cost(row, invoice, indirect_cost_map, invoice_sales_map):
	if not invoice:
		return 0

	indirect_cost = indirect_cost_map.get(invoice, 0)
	if is_invoice_row(row, invoice):
		return indirect_cost

	invoice_sales = flt(invoice_sales_map.get(invoice))
	if not invoice_sales:
		return 0

	return indirect_cost * get_sales_amount(row) / invoice_sales


def get_report_summary(data):
	summary_rows = [row for row in data if not cint(row.get("indent"))]
	net_sales = sum(get_sales_amount(row) for row in summary_rows)
	direct_cost = sum(flt(row.direct_cost) for row in summary_rows)
	gross_profit = sum(flt(row.get("gross_profit")) for row in summary_rows)
	indirect_cost = sum(flt(row.indirect_cost) for row in summary_rows)
	net_profit = sum(flt(row.net_profit) for row in summary_rows)
	profit_percent = (net_profit / net_sales * 100) if net_sales else 0

	return [
		{"value": net_sales, "label": _("Net Sales"), "datatype": "Currency"},
		{"value": direct_cost, "label": _("Direct Cost"), "datatype": "Currency"},
		{"value": gross_profit, "label": _("Gross Profit"), "datatype": "Currency"},
		{"value": indirect_cost, "label": _("Indirect Cost"), "datatype": "Currency"},
		{"value": net_profit, "label": _("Net Profit"), "datatype": "Currency"},
		{"value": profit_percent, "label": _("Net Profit %"), "datatype": "Percent"},
	]


def get_chart(data):
	summary_rows = [row for row in data if not cint(row.get("indent"))]

	return {
		"data": {
			"labels": [_("Net Sales"), _("Direct Cost"), _("Gross Profit"), _("Indirect Cost"), _("Net Profit")],
			"datasets": [
				{
					"name": _("Amount"),
					"values": [
						sum(get_sales_amount(row) for row in summary_rows),
						sum(flt(row.direct_cost) for row in summary_rows),
						sum(flt(row.get("gross_profit")) for row in summary_rows),
						sum(flt(row.indirect_cost) for row in summary_rows),
						sum(flt(row.net_profit) for row in summary_rows),
					],
				}
			],
		},
		"type": "bar",
	}
