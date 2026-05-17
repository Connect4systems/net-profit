frappe.query_reports["Net Profit"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "sales_invoice",
			label: __("Sales Invoice"),
			fieldtype: "Link",
			options: "Sales Invoice",
			get_query() {
				const company = frappe.query_report.get_filter_value("company");
				const customer = frappe.query_report.get_filter_value("customer");

				return {
					filters: {
						...(company ? { company } : {}),
						...(customer ? { customer } : {}),
						docstatus: 1,
					},
				};
			},
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: ["Invoice", "Item Code", "Item Group", "Customer", "Customer Group", "Territory", "Sales Person", "Project"],
			default: "Invoice",
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
		},
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "include_returned_invoices",
			label: __("Include Returned Invoices"),
			fieldtype: "Check",
			default: 1,
		},
	],
};
