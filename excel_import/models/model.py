from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class IncoiceExcelReport(models.TransientModel):
    _name = "invoice.report.wizard"
    _description = "Invoice Report"

    from_date = fields.Datetime("From Date" , required=True)
    to_date = fields.Datetime("To Date")

    @api.constrains('from_date')
    def check_from_date(self):
        for record in self:
            if record.from_date:
                from_date = fields.Datetime.to_datetime(record.from_date)
                comparison_date = datetime(2023, 11, 1)
                if from_date <= comparison_date:
                    raise UserError("From date must be greater than November 1, 2023.")
            # date = record.from_date.date()
            # if date <= datetime(2023, 11,1).date():
            #     raise UserError("From date must be greater than November 1, 2023.")

    def action_export(self):

        # domain = [('move_type', '=', 'out_invoice')]
        domain = []

        if self.from_date:
            domain += [('create_date', '>=', self.from_date)]
        if self.to_date:
            domain += [('create_date', '<=', self.to_date)]

        # invoices = self.env['account.move'].search_read(domain)

        invoices = self.env['split.initial.invoice'].search(domain)
        data_to_export = []
        currency_rate = []
        for invoice in invoices:
            # invoice_currency = self.env['account.move'].search([('name', '=', invoice.name)])
            #
            # if invoice_currency:
            #     for currency in invoice_currency:
            if invoice.invoice_id.current_currency_rate:
                currency_rate = invoice.invoice_id.current_currency_rate
            else:
                currency_rate = invoice.invoice_id.old_currency_rate

            lines_data = []
            for line in invoice.order_line:
                lines_data.append({

                    # 'item_code': line.itemcode,
                    # 'item_description': currency_rate,
                    # 'item_hsn': line.hsnorsaccode,
                    # 'categorylvl1': line.categorylvl1,
                    # 'categorylvl2': line.categorylvl2,
                    # 'category': line.category,
                    # 'category_group': line.categorygrp,
                    # 'category_sub_group': line.subgrp,
                    # 'product': line.product_id.name,
                    # 'uom': line.unitofmeasurement,
                    # 'quantity': line.quantity,
                    # 'qty_in_ctn': line.qtyinctn,
                    # 'item_price': line.itemprice,
                    # 'rate_per_kg': line.rateperkgusd,
                    # 'gross_amount': line.grossamount,
                    # 'net_amount_in_usd': line.netamtinusdfob,
                    # 'item_discount': line.itemdiscountamount,
                    # 'total_in_usd': line.amtinusd,
                    # 'item_total_amount': line.itemtotalamount,
                    # 'gst_rate': line.gstrate,
                    # 'igst_amount': line.igstamount,

                })

            data_to_export.append({
                'invoice_number': invoice.name,
                'invoice_date': currency_rate,

                # 'supplier_name': invoice.supplierlegalname,
                # 'supplier_address1': invoice.supplieraddress1,
                # 'recipient_legal_name': invoice.recipientlegalname,
                # 'recipient_address1': invoice.recipientaddress1,
                # 'recipient_address2': invoice.recipientaddress2,
                # 'port_of_discharge': invoice.portofdischarge,
                # 'country_of_final': invoice.countryoffdest,
                # 'final_destination': invoice.findest,
                # 'order_type': invoice.supplytypecode,
                # 'document_date': invoice.documentdate,
                # 'shipping_bill_date': invoice.shippingbilldate,
                # 'shipping_bill_number': invoice.shippingbillnumber,
                # 'currency_rate': invoice.current_currency_rate,
                'lines': lines_data,
                # Add other fields you need from the invoice
            })

        print(data_to_export)
        data = {
            'datas': data_to_export,
        }
        return self.env.ref('excel_import.action_report_invoice_excel').report_action(self,data=data)


