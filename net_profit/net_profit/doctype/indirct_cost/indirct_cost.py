# Copyright (c) 2026, Net Profit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class IndirctCost(Document):
	def validate(self):
		self.validate_expinses()

	def on_submit(self):
		if self.journal_entry:
			return

		journal_entry = self.create_journal_entry()
		self.db_set("journal_entry", journal_entry.name, update_modified=False)

	def on_cancel(self):
		if not self.journal_entry:
			return

		journal_entry = frappe.get_doc("Journal Entry", self.journal_entry)
		if journal_entry.docstatus == 1:
			journal_entry.cancel()

	def validate_expinses(self):
		if not self.payment_account:
			frappe.throw(_("Payment Account is required."))

		if not self.expinses:
			frappe.throw(_("At least one expense row is required."))

		for row in self.expinses:
			if not row.account:
				frappe.throw(_("Account is required in row {0}.").format(row.idx))

			if flt(row.amount) <= 0:
				frappe.throw(_("Amount must be greater than zero in row {0}.").format(row.idx))

	def create_journal_entry(self):
		company = self.get_company()
		total_amount = sum(flt(row.amount) for row in self.expinses)

		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Journal Entry"
		journal_entry.company = company
		journal_entry.posting_date = self.date
		journal_entry.user_remark = _("Indirct Cost for invoice {0}").format(self.sales_invoice)

		for row in self.expinses:
			journal_entry.append(
				"accounts",
				{
					"account": row.account,
					"debit_in_account_currency": flt(row.amount),
					"credit_in_account_currency": 0,
					"user_remark": row.description,
				},
			)

		journal_entry.append(
			"accounts",
			{
				"account": self.payment_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": total_amount,
			},
		)

		journal_entry.insert()
		journal_entry.submit()

		return journal_entry

	def get_company(self):
		if self.sales_invoice:
			company = frappe.db.get_value("Sales Invoice", self.sales_invoice, "company")
			if company:
				return company

		company = frappe.db.get_value("Account", self.payment_account, "company")
		if company:
			return company

		frappe.throw(_("Could not determine company from Sales Invoice or Payment Account."))
