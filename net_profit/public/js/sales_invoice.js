frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Indirct Cost"), () => {
			frappe.new_doc("Indirct Cost", {
				sales_invoice: frm.doc.name,
			});
		}, __("Create"));
	},
});
