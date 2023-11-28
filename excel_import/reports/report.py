# -*- coding: utf-8 -*-

import base64
import io
from odoo import models


class InvoiceExcelXlsx(models.AbstractModel):
    _name = 'report.excel_import.action_report_invoice_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, patients):
        print("ecccccc",data['datas'])

        sheet = workbook.add_worksheet("Invoices")
        bold = workbook.add_format({'bold': True})
        sheet.set_column('A:Z', 15)
        # sheet.set_column('E:F', 13)

        row = 0
        col = 0

        sheet.write(row, col, 'Document Number', bold)
        sheet.write(row, col+1, 'Select Products/line Number', bold)
        sheet.write(row, col+2, 'Ship From Location', bold)
        sheet.write(row, col+3, 'Supplier Legal Name', bold)
        sheet.write(row, col+4, 'Supplier Address 1', bold)
        sheet.write(row, col+5, 'Recipient Legal Name', bold)
        sheet.write(row, col+6, 'Recipient Address 1', bold)
        sheet.write(row, col+7, 'Recipient Address 2', bold)
        sheet.write(row, col+8, 'Port of Discharge', bold)
        sheet.write(row, col+9, 'Country of Final Destination', bold)
        sheet.write(row, col+10, 'Final Destination', bold)
        sheet.write(row, col+11, 'Order Type', bold)
        sheet.write(row, col+12, 'Item Code', bold)
        sheet.write(row, col+13, 'Selected Product Description', bold)
        sheet.write(row, col+14, 'Selected Product HSN or SAC code', bold)
        sheet.write(row, col+15, 'Selected Product Level 1 Category', bold)
        sheet.write(row, col+16, 'Selected Product Level 2 Category', bold)
        sheet.write(row, col+17, 'Selected Products Category', bold)
        sheet.write(row, col+18, 'Selected Products Category Group', bold)
        # sheet.write(row, col+19, 'Selected Products Category Sub Group', bold)
        sheet.write(row, col+19, 'Selected Products Category Sub Group', bold)
        sheet.write(row, col+20, 'Selected Products/Product', bold)
        sheet.write(row, col+21, 'Selected Products/Unit of Measurement', bold)
        sheet.write(row, col+22, 'Selected Products/Quantity', bold)
        sheet.write(row, col+23, 'Selected Products/Qty in CTN', bold)
        sheet.write(row, col+24, 'Selected Products/Item Price', bold)
        sheet.write(row, col+25, 'Selected Products/Rate/Kg in USD', bold)
        sheet.write(row, col+26, 'Selected Products/Gross Amount/ INR Line Amt', bold)
        sheet.write(row, col+27, 'Selected Products/Net AMT in USD', bold)
        # sheet.write(row, col+28, 'Selected Products/Net AMT in USD', bold)
        sheet.write(row, col+28, 'Invoice ID/Currency Rate', bold)
        sheet.write(row, col+29, 'Document Date', bold)
        sheet.write(row, col+30, 'Shipping Bill Date', bold)
        sheet.write(row, col+31, 'Shipping Bill Number', bold)
        sheet.write(row, col+32, 'Selected Products/Item Discount Amount', bold)
        sheet.write(row, col+33, 'Total Net Amount in USD', bold)
        sheet.write(row, col+34, 'Selected Products/Item Total Amount/NR Line Amt', bold)
        sheet.write(row, col+35, 'GST Rate', bold)
        sheet.write(row, col+36, 'IGST Amount', bold)



        for invoices in data['datas']:
            row += 1
            invoice_row = row
            sheet.write(row, col, invoices['invoice_number'])
            sheet.write(row, col + 2, "KOTHAMANGALAM MANUFACTURING PLANT")
            sheet.write(row, col + 3, invoices['invoice_date'])
            # sheet.write(row, col + 4, invoices['supplier_address1'])
            # sheet.write(row, col + 5, invoices['recipient_legal_name'])
            # sheet.write(row, col + 6, invoices['recipient_address1'])
            # sheet.write(row, col + 7, invoices['recipient_address2'])
            # sheet.write(row, col + 8, invoices['port_of_discharge'])
            # sheet.write(row, col + 9, invoices['country_of_final'])
            # sheet.write(row, col + 10, invoices['final_destination'])
            # sheet.write(row, col + 11, invoices['order_type'])
            # sheet.write(row, col + 28, invoices['currency_rate'])
            # sheet.write(row, col + 29, invoices['document_date'])
            # sheet.write(row, col + 30, invoices['shipping_bill_date'])
            # sheet.write(row, col + 31, invoices['shipping_bill_number'])

            for line_data in invoices['lines']:
                # sheet.write(row, col + 12, line_data['item_code'])
                # sheet.write(row, col + 13, line_data['item_description'])
                # sheet.write(row, col + 14, line_data['item_hsn'])
                # sheet.write(row, col + 15, line_data['categorylvl1'])
                # sheet.write(row, col + 16, line_data['categorylvl2'])
                # sheet.write(row, col + 17, line_data['category'])
                # sheet.write(row, col + 18, line_data['category_group'])
                # sheet.write(row, col + 19, line_data['category_sub_group'])
                # sheet.write(row, col + 20, line_data['product'])
                # sheet.write(row, col + 21, line_data['uom'])
                # sheet.write(row, col + 22, line_data['quantity'])
                # sheet.write(row, col + 23, line_data['qty_in_ctn'])
                # sheet.write(row, col + 24, line_data['item_price'])
                # sheet.write(row, col + 25, line_data['rate_per_kg'])
                # sheet.write(row, col + 26, line_data['gross_amount'])
                # sheet.write(row, col + 27, line_data['net_amount_in_usd'])
                # sheet.write(row, col + 32, line_data['item_discount'])
                # sheet.write(row, col + 33, line_data['total_in_usd'])
                # sheet.write(row, col + 34, line_data['item_total_amount'])
                # sheet.write(row, col + 35, line_data['gst_rate'])
                # sheet.write(row, col + 36, line_data['igst_amount'])
                row += 1

            # while invoice_row < row:
            #     # sheet.write(row, col, invoices['invoice_number'])
            #     sheet.write(row, col + 2, "KOTHAMANGALAM MANUFACTURING PLANT")
            #     # sheet.write(row, col + 3, invoices['supplier_name'])
            #     # sheet.write(row, col + 4, invoices['supplier_address1'])
            #     # sheet.write(row, col + 5, invoices['recipient_legal_name'])
            #     # sheet.write(row, col + 6, invoices['recipient_address1'])
            #     # sheet.write(row, col + 7, invoices['recipient_address2'])
            #     # sheet.write(row, col + 8, invoices['port_of_discharge'])
            #     # sheet.write(row, col + 9, invoices['country_of_final'])
            #     # sheet.write(row, col + 10, invoices['final_destination'])
            #     # sheet.write(row, col + 11, invoices['order_type'])
            #     # sheet.write(row, col + 28, invoices['currency_rate'])
            #     # sheet.write(row, col + 29, invoices['document_date'])
            #     # sheet.write(row, col + 30, invoices['shipping_bill_date'])
            #     # sheet.write(row, col + 31, invoices['shipping_bill_number'])
            #     invoice_row += 1






