# -*- codrnng: utf-8 -*-
from odoo import models, fields, api ,_
from odoo.exceptions import UserError,ValidationError
# import cx_Oracle
import collections
import requests
import json
import qrcode
from odoo import tools
import base64
from io import BytesIO
from datetime import datetime
import paramiko
from ftplib import FTP
import io
import pandas as pd


try:
    from num2words import num2words
except ImportError:
    num2words = None

class ResCompany(models.Model):
    _inherit = "res.company"

    signautre = fields.Binary("Signature")

class ProductTempalate(models.Model):
    _inherit = "product.template"

    itemdescription = fields.Char(string="Item Description", )
    istheitemagood = fields.Char(string="Is the item a GOOD (G) or SERVICE (S)", )
    hsnorsaccode = fields.Char(string="HSN or SAC code", )
    quantity = fields.Char(string="Quantity", )
    unitofmeasurement = fields.Char(string="Unit of Measurement", )
    itemprice = fields.Char(string="Item Price", )
    grossamount = fields.Char(string="Gross Amount", )
    itemdiscountamount = fields.Char(string="Item Discount Amount", )
    itemtaxablevalue = fields.Char(string="Item Taxable Value", )
    gstrate = fields.Char(string="GST Rate", )
    igstamount = fields.Char(string="IGST Amount", )
    csgtamount = fields.Char(string="CGST Amount", )
    sgst_utgstamount = fields.Char(string="SGST/UTGST Amount", )
    compcessamountadvalorem = fields.Char(string="Comp Cess Amount Ad Valorem", )
    statecessamountadvalorem = fields.Char(string="State Cess Amount Ad Valorem", )
    otherchargesitemlevel = fields.Char(string="Other Charges (Item Level)", )
    itemtotalamount = fields.Char(string="Item Total Amount", )
    totaltaxablevalue = fields.Char(string="Total Taxable Value", )
    igstamounttotal = fields.Char(string="IGST  Amount Total", )
    cgstamounttotal = fields.Char(string="CGST  Amount Total", )
    sgst_utgstamounttotal = fields.Char(string="SGST/UTGST Amount Total", )
    compcessamounttotal = fields.Char(string="Comp Cess Amount Total", )
    statecessamounttotal = fields.Char(string="State Cess Amount Total", )
    dispercent = fields.Char(string="Discount Percentage", )
    qtyinctn = fields.Char(string="Qty in CTN", )
    amtinusd = fields.Char(string="AMT in USD", )
    netamtinusdfob = fields.Char(string="Net AMT in USD", )
    rateperkgusd = fields.Char(string="Rate/Kg in USD", )


class invoiceInheritanceLine(models.Model):

    _inherit = "account.move.line"

    linenumber = fields.Integer(string="Line Number", )
    itemdescription = fields.Char(string="Item Description", )
    istheitemagood = fields.Char(string="Is the item a GOOD (G) or SERVICE (S)", )
    hsnorsaccode = fields.Char(string="HSN or SAC code", )
    quantity_ = fields.Char(string="Quantity", )
    unitofmeasurement = fields.Char(string="Unit of Measurement", )
    itemprice = fields.Float(string="Item Price", digits=(16, 2), )
    grossamount = fields.Float(string="Gross Amount", digits=(16, 2), )
    itemdiscountamount = fields.Float(string="Item Discount Amount", digits=(16, 2), )
    itemtaxablevalue = fields.Float(string="Item Taxable Value", digits=(16, 2), )
    gstrate = fields.Float(string="GST Rate", digits=(16, 2), )
    igstamount = fields.Float(string="IGST Amount", digits=(16, 2), )
    csgtamount = fields.Float(string="CGST Amount", digits=(16, 2), )
    sgst_utgstamount = fields.Float(string="SGST/UTGST Amount", digits=(16, 2), )
    compcessamountadvalorem = fields.Float(string="Comp Cess Amount Ad Valorem", digits=(16, 2), )
    statecessamountadvalorem = fields.Float(string="State Cess Amount Ad Valorem", digits=(16, 2), )
    otherchargesitemlevel = fields.Float(string="Other Charges (Item Level)", digits=(16, 2), )
    itemtotalamount = fields.Float(string="Item Total Amount", digits=(16, 2), )
    totaltaxablevalue = fields.Float(string="Total Taxable Value", digits=(16, 2), )
    igstamounttotal = fields.Float(string="IGST  Amount Total", digits=(16, 2), )
    cgstamounttotal = fields.Float(string="CGST  Amount Total", digits=(16, 2), )
    sgst_utgstamounttotal = fields.Float(string="SGST/UTGST Amount Total", digits=(16, 2), )
    compcessamounttotal = fields.Float(string="Comp Cess Amount Total", digits=(16, 2), )
    statecessamounttotal = fields.Float(string="State Cess Amount Total", digits=(16, 2), )
    dispercent = fields.Char(string="Discount Percentage", )
    qtyinctn = fields.Char(string="Qty in CTN", )
    amtinusd = fields.Char(string="AMT in USD", )
    netamtinusdfob = fields.Char(string="Net AMT in USD", )
    rateperkgusd = fields.Char(string="Rate/Kg in USD", )

    splitted = fields.Boolean("Splitted")

#     #### new Field
    discamtinusd = fields.Char("Discount AMT in USD")
    categorylvl1 = fields.Char("LEVEL-1 Category")
    categorylvl2 = fields.Char("LEVEL-2 Category")
    category = fields.Char("Category")
    categorygrp = fields.Char("Category Group")
    subgrp = fields.Char("Category Sub-Group")





class invoiceInheritance(models.Model):

    _inherit = "account.move"

    previous_abbr = fields.Char("abbreviation")
    documentdate = fields.Char(string="Document Date",)
    documentnumber = fields.Char(string="Document Number",)
    documenttypecode = fields.Char(string="Document Type Code", )
    supplytypecode = fields.Char(string="Supply Type Code", )
    recipientlegalname = fields.Char(string="Recipient Legal Name", )
    recipienttradename = fields.Char(string="Recipient Trade Name", )
    recipientgstin = fields.Char(string="Recipient GSTIN", )
    placeofsupply = fields.Char(string="Place of Supply", )
    recipientaddress1 = fields.Char(string="Recipient Address 1", )
    recipientplace = fields.Char(string="Recipient Place", )
    recipientstatecode = fields.Char(string="Recipient State Code", )
    recipientpincode = fields.Char(string="Recipient PIN Code", )
    slno = fields.Char(string="Sl No", )
    itemdescription = fields.Char(string="Item Description", )
    istheitemagood = fields.Char(string="Is the item a GOOD (G) or SERVICE (S)", )
    hsnorsaccode = fields.Char(string="HSN or SAC code", )
    quantity = fields.Char(string="Quantity", )
    unitofmeasurement = fields.Char(string="Unit of Measurement", )
    itemprice = fields.Char(string="Item Price", )
    grossamount = fields.Char(string="Gross Amount", )
    itemdiscountamount = fields.Char(string="Item Discount Amount", )
    itemtaxablevalue = fields.Char(string="Item Taxable Value", )
    gstrate = fields.Char(string="GST Rate", )
    igstamount = fields.Char(string="IGST Amount", )
    csgtamount = fields.Char(string="CGST Amount", )
    sgst_utgstamount = fields.Char(string="SGST/UTGST Amount", )
    compcessamountadvalorem = fields.Char(string="Comp Cess Amount Ad Valorem", )
    statecessamountadvalorem = fields.Char(string="State Cess Amount Ad Valorem", )
    otherchargesitemlevel = fields.Char(string="Other Charges (Item Level)", )
    itemtotalamount = fields.Char(string="Item Total Amount", )
    totaltaxablevalue = fields.Char(string="Total Taxable Value", )
    igstamounttotal = fields.Char(string="IGST  Amount Total", )
    cgstamounttotal = fields.Char(string="CGST  Amount Total", )
    sgst_utgstamounttotal = fields.Char(string="SGST/UTGST Amount Total", )
    compcessamounttotal = fields.Char(string="Comp Cess Amount Total", )
    statecessamounttotal = fields.Char(string="State Cess Amount Total", )
    otherchargeinvoicelevel = fields.Char(string="Other Charge (Invoice Level)", )
    roundoffamount = fields.Char(string="Round Off Amount", )
    totalinvoicevalueininr = fields.Char(string="Total Invoice Value in INR", )
    isreversechargeapplicable = fields.Char(string="Is reverse charge applicable", )
    igstactapplicability = fields.Char(string="Is Sec 7 , IGST Act applicable?", )
    precedingdocumentnumber = fields.Char(string="Preceding Document Number", )
    precedingdocumentdate = fields.Char(string="Preceding Document Date", )
    supplierlegalname = fields.Char(string="Supplier Legal Name", )
    gstinofsupplier = fields.Char(string="GSTIN of Supplier", )
    supplieraddress1 = fields.Char(string="Supplier Address 1", )
    supplierplace = fields.Char(string="Supplier Place", )
    supplierstatecode = fields.Char(string="Supplier State Code", )
    supplierpincode = fields.Char(string="Supplier PIN Code",)
    typeofexport = fields.Char(string="Type of Export",)
    shippingportcode = fields.Char(string="Shipping Port Code", )
    shippingbillnumber = fields.Char(string="Shipping Bill Number", )
    shippingbilldate = fields.Char(string="Shipping Bill Date", )
    payeename = fields.Char(string="Payee Name", )
    payeebankaccountnumber = fields.Char(string="Payee Bank Account Number", )
    modeofpayment = fields.Char(string="Mode of Payment", )
    bankbranchcode = fields.Char(string="Bank Branch Code", )
    paymentterms = fields.Char(string="Payment Terms", )
    paymentinstruction = fields.Char(string="Payment Instruction", )
    credittransferterms = fields.Char(string="Credit Transfer Terms", )
    directdebitterms = fields.Char(string="Direct Debit Terms", )
    creditdays = fields.Char(string="Credit Days", )
    shiptolegalname = fields.Char(string="Ship To Legal Name", )
    shiptogstin = fields.Char(string="Ship To GSTIN", )
    shiptoaddress1 = fields.Char(string="Ship To Address1", )
    shiptoplace = fields.Char(string="Ship To Place", )
    shiptopincode = fields.Char(string="Ship To Pincode", )
    shiptostatecode = fields.Char(string="Ship To State Code", )
    dispatchfromname = fields.Char(string="Dispatch From Name", )
    dispatchfromaddress1 = fields.Char(string="Dispatch From Address1", )
    dispatchfromplace = fields.Char(string="Dispatch From Place", )
    dispatchfromstatecode = fields.Char(string="Dispatch From State Code", )
    dispatchfrompincode = fields.Char(string="Dispatch From Pincode", )
    taxscheme = fields.Char(string="Tax Scheme", )
    transporterid = fields.Char(string="Transporter ID", )
    transmode = fields.Char(string="Trans Mode", )
    transdistance = fields.Char(string="Trans Distance", )
    transportername = fields.Char(string="Transporter Name", )
    transdocno = fields.Char(string="Trans Doc No.", )
    transdocdate = fields.Char(string="Trans Doc Date", )
    vehicleno = fields.Char(string="Vehicle No.", )
    vehicletype = fields.Char(string="Vehicle Type", )
    receiptadvicereference = fields.Char(string="Receipt Advice Reference", )
    receiptadvicedate = fields.Char(string="Receipt Advice Date", )
    tenderorlotreference = fields.Char(string="Tender or Lot Reference", )
    contractreference = fields.Char(string="Contract Reference", )
    externalreference = fields.Char(string="External Reference", )
    projectreference = fields.Char(string="Project Reference", )
    poreferencenumber = fields.Char(string="PO Reference Number", )
    poreferencedate = fields.Char(string="PO Reference Date", )
    additionalsupportingdocumentsurl = fields.Char(string="Additional Supporting Documents URL", )
    additionalinformation = fields.Char(string="Additional Information", )
    documentperiodstartdate = fields.Char(string="Document Period Start Date", )
    documentperiodenddate = fields.Char(string="Document Period End Date", )
    additionalcurrencycode = fields.Char(string="Additional Currency Code", )
    barcode = fields.Char(string="Barcode", )
    freequantity = fields.Char(string="Free Quantity",)
    pretaxvalue = fields.Char(string="Pre-Tax Value",)
    compcessrateadvalorem = fields.Char(string="Comp Cess Rate, Ad Valorem", )
    compcessamountnonadvalorem = fields.Char(string="Comp Cess Amount Non Ad Valorem", )
    statecessrateadvalorem = fields.Char(string="State Cess Rate Ad Valorem", )
    statecessamountnonadvalorem = fields.Char(string="State Cess Amount Non Ad Valorem", )
    purchaseorderlinereference = fields.Char(string="Purchase Order Line Reference", )
    origincountrycode = fields.Char(string="Origin Country Code", )
    uniqueserialnumber = fields.Char(string="Unique Serial Number", )
    batchnumber = fields.Char(string="Batch Number", )
    batchexpirydate = fields.Char(string="Batch Expiry Date", )
    warrantydate = fields.Char(string="Warranty Date", )
    attributename = fields.Char(string="Attribute Name", )
    attributevalue = fields.Char(string="Attribute Value", )
    countrycodeofexport = fields.Char(string="Country Code of Export", )
    recipientphone = fields.Char(string="Recipient Phone", )
    recipientemailid = fields.Char(string="Recipient e-mail ID", )
    recipientaddress2 = fields.Char(string="Recipient Address 2", )
    totalinvoicevalueinfcnr = fields.Char(string="Total Invoice Value in FCNR", )
    paidamount = fields.Char(string="Paid Amount", )
    amountdue = fields.Char(string="Amount Due", )
    discountamountinvoicelevel = fields.Char(string="Discount Amount Invoice Level", )
    tradenameofsupplier = fields.Char(string="Trade Name of Supplier", )
    supplieraddress2 = fields.Char(string="Supplier Address 2", )
    supplierphone = fields.Char(string="Supplier Phone", )
    supplieremail = fields.Char(string="Supplier e-mail", )
    shiptotradename = fields.Char(string="Ship To Trade Name", )
    shiptoaddress2 = fields.Char(string="Ship To Address2", )
    dispatchfromaddress2 = fields.Char(string="Dispatch From Address2", )
    remarks = fields.Char(string="Remarks", )
    exportdutyamount = fields.Char(string="Export Duty Amount", )
    suppliercanoptrefund = fields.Char(string="Supplier Can Opt Refund", )
    ecomgstin = fields.Char(string="ECOM GSTIN", )
    otherreference = fields.Char(string="Other Reference", )

    buyerothcons = fields.Char(string="Buyer Other than Consinee", )
    cerno = fields.Char(string="CER No", )
    cinno = fields.Char(string="CIN No", )
    panno = fields.Char(string="PAN No", )
    iecodeno = fields.Char(string="IE Code No", )
    lutno = fields.Char(string="LUT No", )
    vesselflightno = fields.Char(string="Vessel/Flight No", )
    portofloading = fields.Char(string="Port Of Loading", )
    portofdischarge = fields.Char(string="Port of Discharge", )
    countryoforigin = fields.Char(string="Country of Origin of Goods", )
    countryoffdest = fields.Char(string="Country of Final Destination", )
    termofdelpmnt = fields.Char(string="Term Of Delivery & Payment", )
    findest = fields.Char(string="Final Destination", )
    noofpkgs = fields.Char(string="No & Kind of Packages", )
    dispercent = fields.Char(string="Discount Percentage", )
    qtyinctn = fields.Char(string="Qty in CTN", )
    amtinusd = fields.Char(string="AMT in USD", )
    netamtinusdfob = fields.Char(string="Net AMT in USD", )
    rateperkgusd = fields.Char(string="Rate/Kg in USD", )

    # sum amount compute fields
    total_assesable_value = fields.Float(string="Total AssAmount", compute='_compute_total_assesable_value', store=True)
    total_igst_value = fields.Float(string="Total Igst Value", compute='_compute_total_igst_value', store=True)
    total_discount_val = fields.Float(string="Total Discount Value", compute='_compute_total_discount_val', store=True)
    total_invoice_val = fields.Float(string="Total Invoice Value", compute='_compute_total_invoice_val', store=True)

    # new field for exchange rate
    old_currency_rate = fields.Char(string="Old Currency Rate")
    current_currency_rate = fields.Float(string="Currency Rate")


    def calc_currency_rate(self):
        print("hiii")
    @api.onchange('current_currency_rate')
    def onchange_current_currency_rate(self):
        # print("Onchanged")
        if self.current_currency_rate != 0:
        # print(self.amtinusd)
            for lines in self.invoice_line_ids:
                # print("USD total amt",lines.amtinusd)
                # print("usd unit price",lines.rateperkgusd)
                # print("HSN code",lines.rateperkgusd)
                # print("usd disc amount",lines.discamtinusd)
                if lines.itemprice:
                    # (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
                    # lines.itemprice = (float(lines.netamtinusdfob)+float(lines.discamtinusd)) /lines.quantity * float(self.current_currency_rate)


                    lines.itemprice = float(lines.rateperkgusd) * float(self.current_currency_rate)
                    # row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
                    lines.grossamount = float(lines.itemprice) * float(lines.quantity)
                    # lines.grossamount = ((float(lines.netamtinusdfob)+float(lines.discamtinusd))
                    #                       * float(self.current_currency_rate))
                    lines.itemdiscountamount = float(lines.discamtinusd) * float(self.current_currency_rate)
                    lines.itemtaxablevalue = (float(lines.itemprice) * float(lines.quantity))-lines.itemdiscountamount
                    lines.igstamount = (float(lines.itemtaxablevalue)* float(lines.gstrate)/100)
                    lines.itemtotalamount = float(lines.itemtaxablevalue) + float( lines.igstamount)

                    # lines.totaltaxablevalue = float(lines.itemprice) * float(lines.quantity)
                    lines.totaltaxablevalue =  lines.itemtaxablevalue
                    lines.igstamounttotal= (float(lines.itemtaxablevalue)* float(lines.gstrate)/100)



    # ####################################################################

    @api.depends('invoice_line_ids')
    def _compute_total_assesable_value(self):
        for record in self:
            total_assesable = 0
            for line in record.invoice_line_ids:
                total_assesable = total_assesable + line.itemtaxablevalue
                record.total_assesable_value = total_assesable

    @api.depends('invoice_line_ids')
    def _compute_total_igst_value(self):
        for record in self:
            total_igst = 0
            for line in record.invoice_line_ids:
                total_igst = total_igst + line.igstamount
                record.total_igst_value = total_igst

    @api.depends('invoice_line_ids')
    def _compute_total_discount_val(self):
        for record in self:
            total_discount = 0
            for line in record.invoice_line_ids:
                total_discount = total_discount + line.itemdiscountamount
                record.total_discount_val = total_discount

    @api.depends('invoice_line_ids')
    def _compute_total_invoice_val(self):
        for record in self:
            total_invoice = 0
            for line in record.invoice_line_ids:
                total_invoice = total_invoice + line.itemtotalamount
                record.total_invoice_val = total_invoice

class InvoiceSummaryLine(models.Model):
    _name = 'invoice.summary.line'

    summary_name = fields.Char("Invoice Summary Name")
    amt_in_inr = fields.Float("Amount IN INR")
    igst_amount  = fields.Float("IGST Amount")
    gst_rate = fields.Float("Gst Rate")
    splitted_invoice = fields.Many2one('split.initial.invoice',string="Splitted Invoice")



class SplitInitialInvoice(models.Model):
    _name = 'split.initial.invoice'

    def unlink(self):
        for record in self:
            if record.irn:
                raise UserError("Error Unable to delete IRN Generated Invoice")
            for products in record.order_line:
                products.move_line_id.splitted= False
        return super(SplitInitialInvoice, self).unlink()
    # @api.model
    # def compute_ageing(self, data):
    #     """Redirects to the report with the values obtained from the wizard
    #             'data['form']':  date duration"""
    #     # rec = self.browse(data)
    #     data = {}
    #     # data['form'] = rec.read(['from_date', 'product_categ', 'user_id'])
    #     return self.env.ref('invoice_split_custom.report_split_invoice').report_action(rec, data=data)

    @api.depends('irn')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.irn)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image


    name = fields.Char('Name')
    splitted_date = fields.Datetime(string="Created Date")
    invoice_id = fields.Many2one('account.move',string='Invoice ID')
    partner_id = fields.Many2one('res.partner',string='Customer')
    order_line = fields.One2many('split.initial.invoice.line','split_invoice',string='Selected Products')
    manufacturer_line = fields.One2many('supporting.manufacturer.line', 'split_invoice',string='Manufacturer Line')
    invoice_summary_line = fields.One2many('invoice.summary.line','splitted_invoice',compute= '_compute_invoice_summary_line',store = True ,string='Invoice Summary Line')

    #qr code

    qr_code = fields.Binary("QR Code", attachment=True, store=True)
    irn = fields.Text("IRN")
    log = fields.Text("Log")
    govt_log = fields.Text("Govt Log")

    #oracle fields
    documentdate = fields.Char(string="Document Date", )
    documentnumber = fields.Char(string="Document Number", )
    documenttypecode = fields.Char(string="Document Type Code", )
    supplytypecode = fields.Char(string="Supply Type Code", )
    recipientlegalname = fields.Char(string="Recipient Legal Name", )
    recipienttradename = fields.Char(string="Recipient Trade Name", )
    recipientgstin = fields.Char(string="Recipient GSTIN", )
    placeofsupply = fields.Char(string="Place of Supply", )
    recipientaddress1 = fields.Char(string="Recipient Address 1", )
    recipientplace = fields.Char(string="Recipient Place", )
    recipientstatecode = fields.Char(string="Recipient State Code", )
    recipientpincode = fields.Char(string="Recipient PIN Code", )
    slno = fields.Char(string="Sl No", )

    itemdescription = fields.Char(string="Item Description", )
    istheitemagood = fields.Char(string="Is the item a GOOD (G) or SERVICE (S)", )
    hsnorsaccode = fields.Char(string="HSN or SAC code", )
    quantity = fields.Char(string="Quantity", )
    unitofmeasurement = fields.Char(string="Unit of Measurement", )
    itemprice = fields.Char(string="Item Price", )
    grossamount = fields.Char(string="Gross Amount", )
    itemdiscountamount = fields.Char(string="Item Discount Amount", )
    itemtaxablevalue = fields.Char(string="Item Taxable Value", )
    gstrate = fields.Char(string="GST Rate", )
    igstamount = fields.Char(string="IGST Amount", )
    csgtamount = fields.Char(string="CGST Amount", )
    sgst_utgstamount = fields.Char(string="SGST/UTGST Amount", )
    compcessamountadvalorem = fields.Char(string="Comp Cess Amount Ad Valorem", )
    statecessamountadvalorem = fields.Char(string="State Cess Amount Ad Valorem", )
    otherchargesitemlevel = fields.Char(string="Other Charges (Item Level)", )
    itemtotalamount = fields.Char(string="Item Total Amount", )
    totaltaxablevalue = fields.Char(string="Total Taxable Value", )
    igstamounttotal = fields.Char(string="IGST  Amount Total", )
    cgstamounttotal = fields.Char(string="CGST  Amount Total", )
    sgst_utgstamounttotal = fields.Char(string="SGST/UTGST Amount Total", )
    compcessamounttotal = fields.Char(string="Comp Cess Amount Total", )
    statecessamounttotal = fields.Char(string="State Cess Amount Total", )

    otherchargeinvoicelevel = fields.Char(string="Other Charge (Invoice Level)", )
    roundoffamount = fields.Char(string="Round Off Amount", )
    totalinvoicevalueininr = fields.Char(string="Total Invoice Value in INR", )
    isreversechargeapplicable = fields.Char(string="Is reverse charge applicable", )
    igstactapplicability = fields.Char(string="Is Sec 7 , IGST Act applicable?", )
    precedingdocumentnumber = fields.Char(string="Preceding Document Number", )
    precedingdocumentdate = fields.Char(string="Preceding Document Date", )
    supplierlegalname = fields.Char(string="Supplier Legal Name", )
    gstinofsupplier = fields.Char(string="GSTIN of Supplier", )
    supplieraddress1 = fields.Char(string="Supplier Address 1", )
    supplierplace = fields.Char(string="Supplier Place", )
    supplierstatecode = fields.Char(string="Supplier State Code", )
    supplierpincode = fields.Char(string="Supplier PIN Code", )
    typeofexport = fields.Char(string="Type of Export", )
    shippingportcode = fields.Char(string="Shipping Port Code", )
    shippingbillnumber = fields.Char(string="Shipping Bill Number", )
    shippingbilldate = fields.Char(string="Shipping Bill Date", )
    payeename = fields.Char(string="Payee Name", )
    payeebankaccountnumber = fields.Char(string="Payee Bank Account Number", )
    modeofpayment = fields.Char(string="Mode of Payment", )
    bankbranchcode = fields.Char(string="Bank Branch Code", )
    paymentterms = fields.Char(string="Payment Terms", )
    paymentinstruction = fields.Char(string="Payment Instruction", )
    credittransferterms = fields.Char(string="Credit Transfer Terms", )
    directdebitterms = fields.Char(string="Direct Debit Terms", )
    creditdays = fields.Char(string="Credit Days", )
    shiptolegalname = fields.Char(string="Ship To Legal Name", )
    shiptogstin = fields.Char(string="Ship To GSTIN", )
    shiptoaddress1 = fields.Char(string="Ship To Address1", )
    shiptoplace = fields.Char(string="Ship To Place", )
    shiptopincode = fields.Char(string="Ship To Pincode", )
    shiptostatecode = fields.Char(string="Ship To State Code", )
    dispatchfromname = fields.Char(string="Dispatch From Name", )
    dispatchfromaddress1 = fields.Char(string="Dispatch From Address1", )
    dispatchfromplace = fields.Char(string="Dispatch From Place", )
    dispatchfromstatecode = fields.Char(string="Dispatch From State Code", )
    dispatchfrompincode = fields.Char(string="Dispatch From Pincode", )
    taxscheme = fields.Char(string="Tax Scheme", )
    transporterid = fields.Char(string="Transporter ID", )
    transmode = fields.Char(string="Trans Mode", )
    transdistance = fields.Char(string="Trans Distance", )
    transportername = fields.Char(string="Transporter Name", )
    transdocno = fields.Char(string="Trans Doc No.", )
    transdocdate = fields.Char(string="Trans Doc Date", )
    vehicleno = fields.Char(string="Vehicle No.", )
    vehicletype = fields.Char(string="Vehicle Type", )
    receiptadvicereference = fields.Char(string="Receipt Advice Reference", )
    receiptadvicedate = fields.Char(string="Receipt Advice Date", )
    tenderorlotreference = fields.Char(string="Tender or Lot Reference", )
    contractreference = fields.Char(string="Contract Reference", )
    externalreference = fields.Char(string="External Reference", )
    projectreference = fields.Char(string="Project Reference", )
    poreferencenumber = fields.Char(string="PO Reference Number", )
    poreferencedate = fields.Char(string="PO Reference Date", )
    additionalsupportingdocumentsurl = fields.Char(string="Additional Supporting Documents URL", )
    additionalinformation = fields.Char(string="Additional Information", )
    documentperiodstartdate = fields.Char(string="Document Period Start Date", )
    documentperiodenddate = fields.Char(string="Document Period End Date", )
    additionalcurrencycode = fields.Char(string="Additional Currency Code", )
    barcode = fields.Char(string="Barcode", )
    freequantity = fields.Char(string="Free Quantity", )
    pretaxvalue = fields.Char(string="Pre-Tax Value", )
    compcessrateadvalorem = fields.Char(string="Comp Cess Rate, Ad Valorem", )
    compcessamountnonadvalorem = fields.Char(string="Comp Cess Amount Non Ad Valorem", )
    statecessrateadvalorem = fields.Char(string="State Cess Rate Ad Valorem", )
    statecessamountnonadvalorem = fields.Char(string="State Cess Amount Non Ad Valorem", )
    purchaseorderlinereference = fields.Char(string="Purchase Order Line Reference", )
    origincountrycode = fields.Char(string="Origin Country Code", )
    uniqueserialnumber = fields.Char(string="Unique Serial Number", )
    batchnumber = fields.Char(string="Batch Number", )
    batchexpirydate = fields.Char(string="Batch Expiry Date", )
    warrantydate = fields.Char(string="Warranty Date", )
    attributename = fields.Char(string="Attribute Name", )
    attributevalue = fields.Char(string="Attribute Value", )
    countrycodeofexport = fields.Char(string="Country Code of Export", )
    recipientphone = fields.Char(string="Recipient Phone", )
    recipientemailid = fields.Char(string="Recipient e-mail ID", )
    recipientaddress2 = fields.Char(string="Recipient Address 2", )
    totalinvoicevalueinfcnr = fields.Char(string="Total Invoice Value in FCNR", )
    paidamount = fields.Char(string="Paid Amount", )
    amountdue = fields.Char(string="Amount Due", )
    discountamountinvoicelevel = fields.Char(string="Discount Amount Invoice Level", )
    tradenameofsupplier = fields.Char(string="Trade Name of Supplier", )
    supplieraddress2 = fields.Char(string="Supplier Address 2", )
    supplierphone = fields.Char(string="Supplier Phone", )
    supplieremail = fields.Char(string="Supplier e-mail", )
    shiptotradename = fields.Char(string="Ship To Trade Name", )
    shiptoaddress2 = fields.Char(string="Ship To Address2", )
    dispatchfromaddress2 = fields.Char(string="Dispatch From Address2", )
    remarks = fields.Char(string="Remarks", )
    exportdutyamount = fields.Char(string="Export Duty Amount", )
    suppliercanoptrefund = fields.Char(string="Supplier Can Opt Refund", )
    ecomgstin = fields.Char(string="ECOM GSTIN", )
    otherreference = fields.Char(string="Other Reference", )

    buyerothcons = fields.Char(string="Buyer Other than Consinee", )
    cerno = fields.Char(string="CER No", )
    cinno = fields.Char(string="CIN No", )
    panno = fields.Char(string="PAN No", )
    iecodeno = fields.Char(string="IE Code No", )
    lutno = fields.Char(string="LUT No", )
    vesselflightno = fields.Char(string="Vessel/Flight No", )
    portofloading = fields.Char(string="Port Of Loading", )
    portofdischarge = fields.Char(string="Port of Discharge", )
    countryoforigin = fields.Char(string="Country of Origin of Goods", )
    countryoffdest = fields.Char(string="Country of Final Destination", )
    termofdelpmnt = fields.Char(string="Term Of Delivery & Payment", )
    findest = fields.Char(string="Final Destination", )
    noofpkgs = fields.Char(string="No & Kind of Packages", )

    dispercent = fields.Float(string="Discount Percentage", )
    qtyinctn = fields.Float(string="Qty in CTN", )
    amtinusd = fields.Float(string="AMT in USD", )
    netamtinusdfob = fields.Float(string="Net AMT in USD", )
    rateperkgusd = fields.Float(string="Rate/Kg in USD", )

    #AdditionalFor3rdPartySupplier
    licdate = fields.Char(string="License Date",)
    supportingmanuname = fields.Char(string="Supporting Manufacturer Name")
    supportingmanuaddress = fields.Char(string="Supporting Manufacturer Address")
    licnumber = fields.Char(string="License Number", )
    exportitem = fields.Char(string="Export Item", )
    exportitemqty = fields.Char(string="Export Item Qty", )
    importitem = fields.Char(string="Import Item", )
    importitemqty = fields.Char(string="Import Item Qty", )

    # sum amount compute fields
    total_assesable_value = fields.Float(string="Total AssAmount", compute='_compute_total_assesable_value', store=True)
    total_igst_value = fields.Float(string="Total IGST Value", compute='_compute_total_igst_value', store=True)
    total_discount_val = fields.Float(string="Total Discount Value", compute='_compute_total_discount_val', store=True)
    total_invoice_val = fields.Float(string="Total Invoice Value", compute='_compute_total_invoice_val', store=True)
    total_value_netamtinusdfob = fields.Float(string="Total Net Amount in USD", compute='_compute_total_value_netamtinusdfob', store=True)

    total_usd_words = fields.Char(string="Total Net Amount in USD", compute='_compute_amount_totalusd_words', store=True)
    total_inr_words = fields.Char(string="Total Net Amount in INR", compute='_compute_amount_totalinr_words', store=True)



    @api.depends('order_line')
    def _compute_total_value_netamtinusdfob(self):
        for record in self:
            total_value_netamtinusdfob = 0
            for line in record.order_line:
                print(type(line.netamtinusdfob))
                total_value_netamtinusdfob = total_value_netamtinusdfob + line.netamtinusdfob
            record.total_value_netamtinusdfob = total_value_netamtinusdfob



    @api.depends('order_line')
    def _compute_invoice_summary_line(self):
        for record in self:
            for order_line in record.order_line:
                summary_name = 'NRECO_'+str(order_line.gstrate)+'%'
                amt_in_inr = order_line.itemtaxablevalue
                igst_amount = order_line.igstamount
                check_inv_sum_line = self.env['invoice.summary.line'].search([('gst_rate','=',order_line.gstrate),('splitted_invoice','=',order_line.split_invoice.id)],limit=1)
                if check_inv_sum_line:
                    inv_sum_dict = {
                        'amt_in_inr':amt_in_inr + check_inv_sum_line.amt_in_inr,
                        'igst_amount':igst_amount + check_inv_sum_line.igst_amount
                        }
                    check_inv_sum_line.write(inv_sum_dict)
                else:
                    inv_sum_dict = {
                        'amt_in_inr': amt_in_inr,
                        'igst_amount': igst_amount,
                        'gst_rate':order_line.gstrate,
                        'summary_name':summary_name,
                        'splitted_invoice':order_line.split_invoice.id
                    }
                    self.env['invoice.summary.line'].create(inv_sum_dict)


    @api.depends('order_line')
    def _compute_total_assesable_value(self):
        for record in self:
            total_assesable = 0
            for line in record.order_line:
                total_assesable = total_assesable + line.itemtaxablevalue
                record.total_assesable_value = total_assesable

    @api.depends('order_line')
    def _compute_total_igst_value(self):
        for record in self:
            total_igst = 0
            for line in record.order_line:
                total_igst = total_igst + line.igstamount
                record.total_igst_value = total_igst

    @api.depends('order_line')
    def _compute_total_discount_val(self):
        for record in self:
            total_discount = 0
            for line in record.order_line:
                total_discount = total_discount + line.itemdiscountamount
                record.total_discount_val = total_discount

    @api.depends('order_line')
    def _compute_total_invoice_val(self):
        for record in self:
            total_invoice = 0
            for line in record.order_line:
                total_invoice = total_invoice + line.itemtotalamount
                record.total_invoice_val = total_invoice

    def amount_to_text(self, amount,currency_id):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang='en_IN').title()
            except NotImplementedError:
                return num2words(number, lang='en_IN').title()

        # if num2words is None:
        #     logging.getLogger(_name_).warning("The library 'num2words' is missing, cannot render textual amounts.")
        #     return ""

        formatted = "%.{0}f".format(currency_id.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)
        lang_code = self.env.context.get('lang') or self.env.user.lang
        lang = self.env['res.lang'].search([('code', '=', lang_code)])
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=currency_id.currency_unit_label,
        )
        if not currency_id.is_zero(amount - integer_value):
            amount_words += ' ' + _('and') + tools.ustr(' {amt_value} {amt_word}').format(
                amt_value=_num2words(fractional_value, lang=lang.iso_code),
                amt_word=currency_id.currency_subunit_label,
            )
        if amount_words:
            amount_words = amount_words
        return amount_words


    @api.depends('order_line')
    def _compute_amount_totalusd_words(self):
        """
        To find amount total in words.
        """
        for record in self:
            currency_id = self.env['res.currency'].search([('name','=','USD')],limit=1)
            if currency_id:
                record.total_usd_words = self.amount_to_text(record.total_value_netamtinusdfob,currency_id)

    @api.depends('order_line')
    def _compute_amount_totalinr_words(self):
        """
        To find amount total in words.
        """
        for record in self:
            currency_id = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
            if currency_id:
                record.total_inr_words = self.amount_to_text(record.total_assesable_value,currency_id)


    ############################## CHANGES #####################
    def retrieve_data_from_sftp(self):
        # SFTP connection details
        hostname = '157.245.102.32'
        port = '22'
        username = 'root'
        password = '!V@C6rgR9Vh'

        # Path to the Excel file on the remote system
        remote_path = "/opt/EasternIRNTest/ODOO-2329400121.xlsx"

        # Establish SSH/SFTP connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, port, username, password)

        # Open SFTP session
        sftp_client = ssh_client.open_sftp()

        # Download the Excel file to a temporary local file
        local_path = "/opt/EasternIRNTest/TEMP_MTR_EXP.xlsx"
        sftp_client.get(remote_path, local_path)

        # Read the Excel file using pandas
        df = pd.read_excel(local_path,dtype={'HSN_CODE':str})
        for index, row in df.iterrows():
            print(row)

            # for row in df:
            # print(row)
            # print(row.INVOICE_NUM)
            # print(row.ODOO_STATUS)
            invoice_obj = self.env['account.move'].search([('name', '=', row.INVOICE_NUM)])
            if not invoice_obj:
                if (row.HL_CITY == None):
                    HL_CITY = ","
                else:
                    HL_CITY = row.HL_CITY

                if (row.HL_ADDRESS3 == None):
                    HL_ADDRESS3 = ","
                else:
                    HL_ADDRESS3 = row.HL_ADDRESS3

                if (row.HL_ADDRESS4 == None):
                    HL_ADDRESS4 = ","
                else:
                    HL_ADDRESS4 = row.HL_ADDRESS4

                EXPORTERS_REF = row.EXPORTERS_REF
                invoice_dict = {
                    # 'type': 'out_invoice',
                    'move_type': 'out_invoice',
                    'name': row.INVOICE_NUM,
                    # 'documentdate': datetime.strptime(EXPORTERS_REF, '%d-%b-%Y').strftime('%d/%m/%Y'),
                    'documentdate': datetime.strptime(EXPORTERS_REF, '%d-%m-%Y').strftime('%d/%m/%Y'),
                    'documentnumber': row.INVOICE_NUM,
                    'documenttypecode': "INV",
                    'supplytypecode': "EXPWP",
                    'recipientlegalname': row.HP_PARTY_NAME,
                    'recipienttradename': row.HP_PARTY_NAME,
                    'recipientgstin': "URP",
                    'placeofsupply': "96",

                    'recipientaddress1': str(row.HL_ADDRESS1) + ',' + str(row.HL_ADDRESS2) + ',',
                    # 'recipientaddress2': row.HL_ADDRESS3 or +',' +','+ row.HL_ADDRESS4 or +',' +','+ row.HL_CITY or False ,
                    'recipientaddress2': str(HL_ADDRESS3) + ',' + str(HL_ADDRESS4) + ',' + str(HL_CITY) or +',',

                    'recipientplace': row.HL_ADDRESS3,
                    'recipientstatecode': "96",
                    'recipientpincode': "999999",
                    'slno': "",

                    'itemdescription': row.DESCRIPTION,
                    'istheitemagood': "G",
                    'hsnorsaccode': row.HSN_CODE,
                    'quantity': row.QTY_IN_KGS,
                    'unitofmeasurement': "KGS",
                    'itemprice': (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
                    'grossamount': row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
                    'itemdiscountamount': row.DISCOUNT_VALUE_IN_INR,
                    'itemtaxablevalue': row.NETVALUE_IN_INR,
                    'gstrate': row.IGST_RATE,
                    'igstamount': row.IGST_PAYABLE,
                    'itemtotalamount': row.NETVALUE_IN_INR + row.IGST_PAYABLE,
                    'totaltaxablevalue': row.NETVALUE_IN_INR,
                    'igstamounttotal': row.IGST_PAYABLE,

                    'totalinvoicevalueininr': row.NETVALUE_IN_INR or row.IGST_PAYABLE,
                    'supplierlegalname': "Eastern Condiments Pvt. Ltd",
                    'gstinofsupplier': row.GSTIN,
                    'supplieraddress1': str(row.ADDRESS_LINE_1) + str(row.ADDRESS_LINE_2) + str(
                        row.ADDRESS_LINE_3) + str(row.LOC_INFORMATION14) + str(row.LOC_INFORMATION15),
                    'supplierplace': row.LOC_INFORMATION15,
                    'supplierstatecode': "32",
                    'supplierpincode': row.POSTAL_CODE,
                    'typeofexport': "EXPWP",
                    'shippingportcode': "INCOK1",
                    'shippingbillnumber': "",
                    'shippingbilldate': "",
                    'shiptolegalname': "India Gateway Terminal Private Limited",
                    'shiptotradename': "India Gateway Terminal Private Limited",
                    'shiptogstin': "URP",
                    'shiptoaddress1': "Administration Building, ICTT,",
                    'shiptoaddress2': "Vallarpadam SEZ, Mulavukadu Village",
                    'shiptoplace': "Ernakulam",
                    'shiptopincode': "682504",
                    'shiptostatecode': "32",

                    # for bill generation

                    'transmode': row.SHIP_METHOD_MEANING,
                    'poreferencenumber': row.CUST_PO_NUMBER,
                    'poreferencedate': row.PO_DATE,
                    'cerno': row.ERC_NO,
                    'cinno': row.CIN,
                    'panno': row.PAN_NO,
                    'iecodeno': row.IE_CODE_NO,
                    'lutno': "AD320222011128W dtd 28/02/2022",
                    'vesselflightno': row.VESSEL_FLIGHT_NO,
                    'portofloading': row.PORT_OF_LOADING,
                    'portofdischarge': row.PORT_OF_DIS,
                    'countryoforigin': row.COUNTRY_OF_ORGN,
                    'countryoffdest': row.COUNTRY_OF_FDEST,
                    'termofdelpmnt': row.TERM_DEL_PMNT,
                    'findest': row.FIN_DEST,
                    'noofpkgs': row.NO_K_OF_PKGS,
                    'buyerothcons': row.BUYER_OTH_CONS,

                    ####### NEW FIELD FOR EXCHANGE RATE
                    'old_currency_rate':row.EXCHANGE_RATE,

                }

                invoice_obj = self.env['account.move'].create(invoice_dict)
            duplicate_product = self.env['account.move.line'].search(
                [('itemdescription', '=', row.DESCRIPTION), ('move_id', '=', invoice_obj.id)])
            print(duplicate_product, "duplicate product")
            if not duplicate_product:
                product_line_dict = {
                    'name': row.DESCRIPTION,
                    'list_price': row.NETVALUE_IN_INR,
                }
                product_created = self.env['product.template'].create(product_line_dict)
                product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product_created.id)])
                print(product_variant, "product tmpl")
                invoice_move_line_dict = {
                    'product_id': product_variant.id,
                    'move_id': invoice_obj.id,
                    'account_id': 7,

                    'linenumber': row.LINE_NUMBER,
                    'itemdescription': row.DESCRIPTION,
                    'istheitemagood': "G",
                    'hsnorsaccode': row.HSN_CODE,
                    'quantity': row.QTY_IN_KGS,
                    'unitofmeasurement': "KGS",
                    'itemprice': (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
                    'grossamount': row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
                    'itemdiscountamount': row.DISCOUNT_VALUE_IN_INR,
                    'itemtaxablevalue': row.NETVALUE_IN_INR,
                    'gstrate': row.IGST_RATE,
                    'igstamount': row.IGST_PAYABLE,
                    'itemtotalamount': row.NETVALUE_IN_INR + row.IGST_PAYABLE,
                    'totaltaxablevalue': row.NETVALUE_IN_INR,
                    'igstamounttotal': row.IGST_PAYABLE,

                    'dispercent': row.DISCOUNT_PER,
                    'qtyinctn': row.QTY_IN_CTN,
                    'amtinusd': row.AMT,
                    # 'amtinusd' : row.NETVALUE_IN_USD,
                    'netamtinusdfob': row.NETVALUE_IN_USD,
                    'rateperkgusd': row.RATE_PER_KG,
                    'discamtinusd':row.DISCOUNT_VALUE_IN_USD,
                #    new fields additional #################################################
                    'categorylvl1': row.LEVEL_1_CATEGORY,
                    'categorylvl2': row.LEVEL_2_CATEGORY,
                    'category': row.CATEGORY,
                    'categorygrp': row.GROUP,
                    'subgrp': row.SUB_GROUP,

                }
                invoice_line_created = self.env['account.move.line'].create(invoice_move_line_dict)

                #
                #
                # pulled_data.append(row.INVOICE_NUM)
                #
                # print(pulled_data)
            # connection.close()
            # updatecursor = connection.cursor()
            # cursor.execute('UPDATE XXEST_EXPORT_EINVOICE SET ODOO_STATUS = 1')
            # connection.commit()
            # print(updatecursor)
        # df.execute('UPDATE XXEST_EXPORT_EINVOICE SET ODOO_STATUS = 1')
        # connection.commit()
        # print("updatedsplit")
        #
        # Print the contents of the Excel file
        # print(df)

        # Close the SFTP session and SSH connection
        sftp_client.close()
        ssh_client.close()

    # ########################


    # def sync_oracle_db(self):
    #     print("enterd oracle sync")
    #     pulled_data = []
    #     connection = cx_Oracle.connect("XXEST_EXPORT_EINVOICE", "xxestexporteinvoice", "172.30.1.142:1531/PROD")
    #     print(connection,"connection successful")
    #     cursor = connection.cursor()
    #     # col_names = [row[0] for row in cursor.description]
    #     # print(cursor,cursor.description)
    #     # cursor.execute('select DBA_TAB_COLUMNS from XXEST_EXPORT_EINVOICE') INVOICE_NUM = 2120700010 ODOO_STATUS = 0
    #     # print(cursor)  ODOO_STATUS = 0
    #     cursor.execute('select * from XXEST_EXPORT_EINVOICE WHERE ODOO_STATUS = 0')  # use triple quotes if you want to spread your query across multiple lines
    #     names = [c[0] for c in cursor.description]
    #     cursor.rowfactory = collections.namedtuple("XXEST_EXPORT_EINVOICE", names)
    #     for row in cursor:
    #         # print(row)
    #         # print(row.INVOICE_NUM)
    #         print(row.ODOO_STATUS)
    #         invoice_obj = self.env['account.move'].search([('name','=',row.INVOICE_NUM)])
    #         if not invoice_obj:
    #             if(row.HL_CITY == None):
    #                 HL_CITY = ","
    #             else:
    #                 HL_CITY = row.HL_CITY
    #
    #             if (row.HL_ADDRESS3 == None):
    #                 HL_ADDRESS3 = ","
    #             else:
    #                 HL_ADDRESS3 = row.HL_ADDRESS3
    #
    #             if (row.HL_ADDRESS4 == None):
    #                 HL_ADDRESS4 = ","
    #             else:
    #                 HL_ADDRESS4 = row.HL_ADDRESS4
    #
    #             EXPORTERS_REF = row.EXPORTERS_REF
    #             invoice_dict = {
    #                 'type': 'out_invoice',
    #                 'name': row.INVOICE_NUM,
    #                 'documentdate': datetime.strptime(EXPORTERS_REF, '%d-%b-%Y').strftime('%d/%m/%Y'),
    #                 'documentnumber': row.INVOICE_NUM,
    #                 'documenttypecode': "INV",
    #                 'supplytypecode': "EXPWP",
    #                 'recipientlegalname': row.HP_PARTY_NAME,
    #                 'recipienttradename': row.HP_PARTY_NAME,
    #                 'recipientgstin': "URP",
    #                 'placeofsupply': "96",
    #
    #
    #                 'recipientaddress1': row.HL_ADDRESS1 +','+ row.HL_ADDRESS2 +',',
    #                 # 'recipientaddress2': row.HL_ADDRESS3 or +',' +','+ row.HL_ADDRESS4 or +',' +','+ row.HL_CITY or False ,
    #                 'recipientaddress2': HL_ADDRESS3 +','+ HL_ADDRESS4 +','+ HL_CITY or +',',
    #
    #                 'recipientplace': row.HL_ADDRESS3 ,
    #                 'recipientstatecode': "96",
    #                 'recipientpincode': "999999",
    #                 'slno': "",
    #
    #
    #                 'itemdescription': row.DESCRIPTION,
    #                 'istheitemagood': "G",
    #                 'hsnorsaccode': row.HSN_CODE,
    #                 'quantity': row.QTY_IN_KGS,
    #                 'unitofmeasurement': "KGS",
    #                 'itemprice': (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
    #                 'grossamount': row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
    #                 'itemdiscountamount': row.DISCOUNT_VALUE_IN_INR,
    #                 'itemtaxablevalue': row.NETVALUE_IN_INR,
    #                 'gstrate': row.IGST_RATE,
    #                 'igstamount': row.IGST_PAYABLE,
    #                 'itemtotalamount': row.NETVALUE_IN_INR + row.IGST_PAYABLE,
    #                 'totaltaxablevalue': row.NETVALUE_IN_INR,
    #                 'igstamounttotal': row.IGST_PAYABLE,
    #
    #                 'totalinvoicevalueininr': row.NETVALUE_IN_INR or row.IGST_PAYABLE,
    #                 'supplierlegalname': "Eastern Condiments Pvt. Ltd",
    #                 'gstinofsupplier': row.GSTIN,
    #                 'supplieraddress1': row.ADDRESS_LINE_1 + row.ADDRESS_LINE_2 + row.ADDRESS_LINE_3 + row.LOC_INFORMATION14 + row.LOC_INFORMATION15,
    #                 'supplierplace': row.LOC_INFORMATION15,
    #                 'supplierstatecode': "32",
    #                 'supplierpincode': row.POSTAL_CODE,
    #                 'typeofexport': "EXPWP",
    #                 'shippingportcode': "INCOK1",
    #                 'shippingbillnumber': "",
    #                 'shippingbilldate': "",
    #                 'shiptolegalname': "India Gateway Terminal Private Limited",
    #                 'shiptotradename': "India Gateway Terminal Private Limited",
    #                 'shiptogstin': "URP",
    #                 'shiptoaddress1': "Administration Building, ICTT,",
    #                 'shiptoaddress2': "Vallarpadam SEZ, Mulavukadu Village",
    #                 'shiptoplace': "Ernakulam",
    #                 'shiptopincode': "682504",
    #                 'shiptostatecode': "32",
    #
    #                 #for bill generation
    #
    #                 'transmode': row.SHIP_METHOD_MEANING,
    #                 'poreferencenumber': row.CUST_PO_NUMBER,
    #                 'poreferencedate': row.PO_DATE,
    #                 'cerno': row.ERC_NO,
    #                 'cinno': row.CIN,
    #                 'panno': row.PAN_NO,
    #                 'iecodeno': row.IE_CODE_NO,
    #                 'lutno': "AD320222011128W dtd 28/02/2022",
    #                 'vesselflightno': row.VESSEL_FLIGHT_NO,
    #                 'portofloading': row.PORT_OF_LOADING,
    #                 'portofdischarge': row.PORT_OF_DIS,
    #                 'countryoforigin': row.COUNTRY_OF_ORGN,
    #                 'countryoffdest': row.COUNTRY_OF_FDEST,
    #                 'termofdelpmnt': row.TERM_DEL_PMNT,
    #                 'findest': row.FIN_DEST,
    #                 'noofpkgs': row.NO_K_OF_PKGS,
    #                 'buyerothcons' : row.BUYER_OTH_CONS,
    #
    #             }
    #
    #             invoice_obj = self.env['account.move'].create(invoice_dict)
    #         duplicate_product = self.env['account.move.line'].search([('itemdescription','=',row.DESCRIPTION),('move_id','=',invoice_obj.id)])
    #         print(duplicate_product,"duplicate product")
    #         if not duplicate_product:
    #             product_line_dict = {
    #                 'name': row.DESCRIPTION,
    #                 'list_price': row.NETVALUE_IN_INR,
    #             }
    #             product_created = self.env['product.template'].create(product_line_dict)
    #             product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product_created.id)])
    #             print(product_variant, "product tmpl")
    #             invoice_move_line_dict = {
    #                 'product_id': product_variant.id,
    #                 'move_id': invoice_obj.id,
    #                 'account_id': 7,
    #
    #                 'linenumber': row.LINE_NUMBER,
    #                 'itemdescription': row.DESCRIPTION,
    #                 'istheitemagood': "G",
    #                 'hsnorsaccode': row.HSN_CODE,
    #                 'quantity': row.QTY_IN_KGS,
    #                 'unitofmeasurement': "KGS",
    #                 'itemprice': (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
    #                 'grossamount': row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
    #                 'itemdiscountamount': row.DISCOUNT_VALUE_IN_INR,
    #                 'itemtaxablevalue': row.NETVALUE_IN_INR,
    #                 'gstrate': row.IGST_RATE,
    #                 'igstamount': row.IGST_PAYABLE,
    #                 'itemtotalamount': row.NETVALUE_IN_INR + row.IGST_PAYABLE,
    #                 'totaltaxablevalue': row.NETVALUE_IN_INR,
    #                 'igstamounttotal': row.IGST_PAYABLE,
    #
    #                 'dispercent' : row.DISCOUNT_PER,
    #                 'qtyinctn' : row.QTY_IN_CTN,
    #                 'amtinusd' : row.AMT,
    #                 # 'amtinusd' : row.NETVALUE_IN_USD,
    #                 'netamtinusdfob' : row.NETVALUE_IN_USD,
    #                 'rateperkgusd' : row.RATE_PER_KG,
    #             }
    #             invoice_line_created = self.env['account.move.line'].create(invoice_move_line_dict)
    #
    #             #
    #             #
    #             # pulled_data.append(row.INVOICE_NUM)
    #             #
    #             # print(pulled_data)
    #         # connection.close()
    #         # updatecursor = connection.cursor()
    #         # cursor.execute('UPDATE XXEST_EXPORT_EINVOICE SET ODOO_STATUS = 1')
    #         # connection.commit()
    #         # print(updatecursor)
    #     cursor.execute('UPDATE XXEST_EXPORT_EINVOICE SET ODOO_STATUS = 1')
    #     connection.commit()
    #     print("updatedsplit")



    def generate_irn(self):
        if not self.shippingbillnumber:
            raise UserError("Enter Shipping Bill Number")
        
        if not self.shippingbilldate:
            raise UserError("Enter Shipping Bill Date")

        if self.shippingbillnumber:            
            print(self,"generate_irn")
            # Production
            url = "https://api-einv.cleartax.in/v2/eInvoice/generate"
            # headers = {"Content-type": "application/json","x-cleartax-auth-token": "1.eb2c06ad-a3b9-4acd-abc8-f73948ece019_f354a14494f3546f98bf2aa67ce0a3a843e08a52ffaedb9c6ec93203da8868a6","x-cleartax-product": "EInvoice", "owner_id": "a41966ae-8da5-4240-8721-96d3f8c89f24","gstin": "32AAACE5276F1ZX"}
            headers = {"Content-type": "application/json","x-cleartax-auth-token": "1.8deef871-4db0-425f-80ae-7ef08034ba05_6f5ad64acceb37bc8a75be8801ad788342b53f158809db451a0acc3a7daacb3a","x-cleartax-product": "EInvoice", "owner_id": "a41966ae-8da5-4240-8721-96d3f8c89f24","gstin": "32AAACE5276F1ZX"}
            
            item_list = []
            count = 1
            itemamtsum = 0
            gstamtsum = 0
            AssVal = 0
            IgstVal= 0
            Discount= 0
            TotInvVal= 0
            for items in self.order_line:
                item_dict = {
                    "SlNo": count,
                    "PrdDesc": items.itemdescription,
                    "IsServc": "N",
                    "HsnCd": items.hsnorsaccode,
                    "Qty": items.quantity,
                    "Unit": "KGS",
                    "UnitPrice": items.itemprice,
                    "TotAmt": items.grossamount,
                    "Discount": items.itemdiscountamount,
                    "AssAmt": items.itemtaxablevalue,
                    "GstRt": items.gstrate,
                    "IgstAmt": items.igstamount,
                    "TotItemVal": items.itemtotalamount,

                }


                count= count + 1
                item_list.append(item_dict)

                AssVal = AssVal + items.itemtaxablevalue
                IgstVal = IgstVal + items.igstamount
                Discount = Discount + items.itemdiscountamount
                TotInvVal = TotInvVal + items.itemtotalamount


                itemamtsum = itemamtsum + items.itemtaxablevalue
                gstamtsum = gstamtsum + items.igstamount
                total_invoice_value = items.itemtotalamount + items.totaltaxablevalue


            formated_original=[
    {
        "transaction": {
        "Version": "1.1",
        "TranDtls": {
            "TaxSch": "GST",
            "SupTyp": "EXPWP",
            "EcmGstin": None,
            "IgstOnIntra": "N"
        },
        "DocDtls": {
            "Typ": "INV",
            "No": "2022900765",
            "Dt": "05/11/2020"
        },
        "SellerDtls": {
            "Gstin": "29AAFCD5862R000",
            "LglNm": "Eastern Condiments Pvt. Ltd",
            "TrdNm": "Eastern Condiments Pvt. Ltd",
            "Addr1": "Branch Code:7IV/1D,IV/1EIRUMALAPADY,PANIPRA P.O.,KOTHAMANGALAM, ERNAKULAM,",
            "Loc": "Eranakulam",
            "Pin": "562160",
            "Stcd": "29",
        },
        "BuyerDtls": {
            "Gstin": "URP",
            "LglNm": "JALEEL DISTRIBUTION LLC",
            "TrdNm": "JALEEL DISTRIBUTION LLC",
            "Pos": "96",
            "Addr1": "P.O.BOX NO : 3262  DUBAI, UNITED ARAB EMIRATES Tel .NO :009714-3339191",
            "Loc": "DUBAI",
            "Pin": "999999",
            "Stcd": "96"
        },
        "ShipDtls": {
            "Gstin": "URP",
            "LglNm": "India Gateway Terminal Private Limited",
            "TrdNm": "India Gateway Terminal Private Limited",
            "Addr1": "Administration Building, ICTT,",
            "Addr2": "Vallarpadam SEZ, Mulavukadu Village",
            "Loc": "Ernakulam",
            "Pin": 562160,
            "Stcd": 29
        },
        "ItemList": [
            {
            "SlNo": 1,
            "PrdDesc": "Hs Code -15131900- 67/12- Coconut Oil 2 Ltr Coconut Oil Bottle",
            "IsServc": "N",
            "HsnCd": "15131900",
            "Qty": 15600.0,
            "Unit": "KG",
            "UnitPrice": 171.22,
            "TotAmt": 2671032.0,
            "Discount": 0.0,
            # "PreTaxVal": 1,
            "AssAmt": 2671032.0,
            "GstRt": 5.0,
            "IgstAmt": 133551.6,
                # 2671032.0
            "TotItemVal": 2804583.6

            }
        ],
        "ValDtls": {
            "AssVal": 2671032.0,
            "IgstVal": 133551.6,
            "Discount": 0,
            "TotInvVal": 2804583.6,
        },
        "ExpDtls": {
            "ShipBNo": "6351151",
            "ShipBDt": "01/08/2020"
        }
        }
    }
    ]
            # testeddate = self.documentdate
            # dt_obj = datetime.strptime(testeddate, '%Y-%m-%d %H:%M:%S')

            #for buyer other than consinee condition in invoice for JALEEL STRATEX
            if(self.buyerothcons):
                buyerotherthanconsinee = "JALEEL STRATEX BR. OF "
            else:
                buyerotherthanconsinee = ""

            formated = [
                {
                    "transaction": {
                        "Version": "1.1",
                        "TranDtls": {
                            "TaxSch": "GST",
                            "SupTyp": "EXPWP",
                            "EcmGstin": None,
                            "IgstOnIntra": "N"
                        },
                        "DocDtls": {
                            "Typ": "INV",
                            "No": self.documentnumber,
                            "Dt": self.documentdate
                        },
                        "SellerDtls": {
                            "Gstin": "32AAACE5276F1ZX",
                            "LglNm": self.supplierlegalname,
                            "TrdNm": self.supplierlegalname,
                            "Addr1": self.supplieraddress1 or "",
                            "Loc": self.supplierplace or "",
                            "Pin": self.supplierpincode,
                            "Stcd": self.supplierstatecode,
                        },
                        "BuyerDtls": {
                            "Gstin": self.recipientgstin,
                            "LglNm": buyerotherthanconsinee + self.recipientlegalname,
                            "TrdNm": buyerotherthanconsinee + self.recipienttradename,
                            "Pos": self.placeofsupply or "",
                            "Addr1": self.recipientaddress1 or "",
                            "Addr2": self.recipientaddress2 or "",
                            "Loc": self.recipientplace or "",
                            "Pin": self.recipientpincode or "",
                            "Stcd": self.recipientstatecode or "",
                        },
                        "ShipDtls": {
                            "Gstin": self.shiptogstin,
                            "LglNm": self.shiptolegalname,
                            "TrdNm": self.shiptotradename,
                            "Addr1": self.shiptoaddress1,
                            "Addr2": self.shiptoaddress2,
                            "Loc": self.shiptoplace,
                            "Pin": self.shiptopincode,
                            "Stcd": self.shiptostatecode
                        },
                        "ItemList": item_list,
                        "ValDtls": {
                            "AssVal": AssVal,
                            "IgstVal":IgstVal ,
                            # "Discount":Discount ,
                            "TotInvVal":TotInvVal ,
                        },
                        "ExpDtls": {
                            "ShipBNo": self.shippingbillnumber or "",
                            "ShipBDt": self.shippingbilldate or "",
                            "Port": self.shippingportcode or "",

                        }
                    }
                }
            ]


            print(formated)
            # print(data,"data1c")
            try:
                req = requests.put(url, data=json.dumps(formated), headers=headers, timeout=50)
                req.raise_for_status()
                content = req.json()
                print(content)
                # print(content[0]['govt_response']['Irn'])
                if content[0]['govt_response']['Success'] == 'Y':
                    self.irn = content[0]['govt_response']['Irn'] if content[0]['govt_response'][
                                                                        'Success'] == 'Y' else False
                    self.govt_log = 'Status: '+ content[0]['govt_response']['Success'] + ', AckNo: '+ str(content[0]['govt_response']['AckNo']) + ', AckDate: '+ str(content[0]['govt_response']['AckDt'])
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(self.irn)
                    qr.make(fit=True)
                    img = qr.make_image()
                    temp = BytesIO()
                    img.save(temp, format="PNG")
                    qr_image = base64.b64encode(temp.getvalue())
                    self.qr_code = qr_image

                else:
                    self.irn = False
                    self.govt_log = content[0]['govt_response']
                    # self.irn = content[0]['govt_response']['Irn'] if content[0]['govt_response']['Success'] == 'Y' else False
                self.log = content[0]['document_status']


            except IOError:
                error_msg = ("Required Fields Missing or Invalid Format For IRN generation.")
                raise self.env['res.config.settings'].get_config_warning(error_msg)
                # raise self.env['res.config.settings'].get_config_warning(formated)

            # for row in cursor:
            #     print(row)

        # def action_view_split(self):
        #     for record in self:
        #         action = self.env.ref('stock.action_picking_tree_all').read()[0]
        #         pickings = self.mapped('pick_ids')
        #         if len(pickings) > 1:
        #             action['domain'] = [('id', 'in', pickings.ids)]
        #         elif pickings:
        #             action['views'] = [(record.env.ref('stock.view_picking_form').id, 'form')]
        #             action['res_id'] = pickings.id
        #     return action
class SupportingManufacturer(models.Model):
    _name = 'supporting.manufacturer.line'

    split_invoice = fields.Many2one('split.initial.invoice', string='Invoice')

    date = fields.Char("Date")
    manufacturer_name = fields.Char("Manufacturer Name")
    manufacturer_address = fields.Char("Manufacturer Address")
    licence_no = fields.Char("Licence No")
    export_item = fields.Char("Export Item")
    export_item_qty = fields.Float("Export Item Qty")
    import_item = fields.Char("Import Item")
    import_item_qty = fields.Float("Import Item Qty")





class SplitInitialInvoiceLine(models.Model):
    _name = 'split.initial.invoice.line'

    move_line_id = fields.Many2one('account.move.line',string="ACCOUNT mOVE Line")
    product_id = fields.Many2one('product.product',string='Product')
    label = fields.Char('Product Description')
    quantity = fields.Float('Quantity')
    price_unit = fields.Float('Price Unit')
    subtotal = fields.Float('Subtotal')
    split_invoice = fields.Many2one('split.initial.invoice',string='Invoice')
    
    linenumber = fields.Integer(string="Line Number", )
    itemdescription = fields.Char(string="Item Description", )
    istheitemagood = fields.Char(string="Is the item a GOOD (G) or SERVICE (S)", )
    hsnorsaccode = fields.Char(string="HSN or SAC code", )
    quantity_ = fields.Float(string="Quantity", digits=(16, 2), )
    unitofmeasurement = fields.Char(string="Unit of Measurement", )
    itemprice = fields.Float(string="Item Price", digits=(16, 2), )
    grossamount = fields.Float(string="Gross Amount", digits=(16, 2), )
    itemdiscountamount = fields.Float(string="Item Discount Amount", digits=(16, 2), )
    itemtaxablevalue = fields.Float(string="Item Taxable Value", digits=(16, 2), )
    gstrate = fields.Float(string="GST Rate", digits=(16, 2), )
    igstamount = fields.Float(string="IGST Amount", digits=(16, 2), )
    csgtamount = fields.Float(string="CGST Amount", digits=(16, 2), )
    sgst_utgstamount = fields.Float(string="SGST/UTGST Amount", digits=(16, 2), )
    compcessamountadvalorem = fields.Float(string="Comp Cess Amount Ad Valorem", digits=(16, 2), )
    statecessamountadvalorem = fields.Float(string="State Cess Amount Ad Valorem", digits=(16, 2), )
    otherchargesitemlevel = fields.Float(string="Other Charges (Item Level)", digits=(16, 2), )
    itemtotalamount = fields.Float(string="Item Total Amount", digits=(16, 2), )
    totaltaxablevalue = fields.Float(string="Total Taxable Value", digits=(16, 2), )
    igstamounttotal = fields.Float(string="IGST  Amount Total", digits=(16, 2), )
    # cgstamounttotal = fields.Float(string="CGST  Amount Total", digits=(16, 2), )
    # sgst_utgstamounttotal = fields.Float(string="SGST/UTGST Amount Total", digits=(16, 2), )
    # compcessamounttotal = fields.Float(string="Comp Cess Amount Total", digits=(16, 2), )
    # statecessamounttotal = fields.Float(string="State Cess Amount Total", digits=(16, 2), )


    dispercent = fields.Float(string="Discount Percentage", digits=(16, 2), )
    qtyinctn = fields.Float(string="Qty in CTN", digits=(16, 2), )
    amtinusd = fields.Float(string="AMT in USD", digits=(16, 2), )
    netamtinusdfob = fields.Float(string="Net AMT in USD", digits=(16, 2), )
    rateperkgusd = fields.Float(string="Rate/Kg in USD", digits=(16, 2), )


################################# Additional fields ############################

    categorylvl1 = fields.Char("LEVEL-1 Category")
    categorylvl2 = fields.Char("LEVEL-2 Category")
    category = fields.Char("Category")
    categorygrp = fields.Char("Category Group")
    subgrp = fields.Char("Category Sub-Group")



class AccountMove(models.Model):
    _inherit = 'account.move'

    splitted_invoices = fields.Many2many('split.initial.invoice', string="Splitted Invoice")
    splitted_invoice_count = fields.Integer(string='Invoice Count', compute='_compute_splitted_invoices_count', readonly=True)

    @api.depends('splitted_invoices')
    def _compute_splitted_invoices_count(self):
        for order in self:
            order.splitted_invoice_count = len(order.splitted_invoices)

    def action_view_split_invoice_custom(self):
        for record in self:
            action = self.env.ref('invoice_split_custom.action_splited_invoice_view').read()[0]
            pickings = self.mapped('splitted_invoices')
            if len(pickings) > 1:
                action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                action['views'] = [(record.env.ref('invoice_split_custom.splited_invoice_view_form').id, 'form')]
                action['res_id'] = pickings.id
        return action
    # # @api.model
    # def compute_order_line(self):
    #     print(self)
    #
    # @api.onchange("order_line")
    # def _onchange_all_partner_ids(self):
    #     print(self.env.context.get('active_id'))
    #     res = {}
    #     res['domain'] = {'order_line': [('move_id', '=',self.env.context.get('active_id')),('exclude_from_invoice_tab','=',False)], }
    #     return res
    #
    #
    # @api.model
    # def compute_ageing(self, data):
    #     """Redirects to the report with the values obtained from the wizard
    #             'data['form']':  date duration"""
    #     rec = self.browse(data)
    #     print(rec)
    #     data = {}
    #     data['form'] = rec.read(['from_date','product_categ', 'user_id'])
    #     return self.env.ref('invoice_split_custom.report_split_invoice').report_action(rec, data=data)
    #

