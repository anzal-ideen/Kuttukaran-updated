# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
# import cx_Oracle
import collections
from datetime import datetime

class AgeingAnalysis(models.TransientModel):
    _name = 'invoice.split'

    from_date = fields.Datetime(string="Starting Date",)
    product_categ = fields.Many2many('product.category', string="Category")
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    order_line = fields.Many2many(comodel_name='account.move.line',string='Select Products')



    @api.onchange("order_line")
    def _onchange_all_partner_ids(self):
        #('splitted', '=', False)
        res = {}
        res['domain'] = {'order_line': [('move_id', '=',self.env.context.get('active_id')),('exclude_from_invoice_tab','=',False),('splitted', '=', False)], }
        return res


    @api.model
    def compute_ageing(self, data):
        """Redirects to the report with the values obtained from the wizard
                'data['form']':  date duration"""
        rec = self.browse(data)
        data = {}
        data['form'] = rec.read(['from_date','product_categ', 'user_id'])
        return self.env.ref('invoice_split_custom.report_split_invoice').report_action(rec, data=data)

    def select_all_invoices(self):
        current_invoice = self.env['account.move'].search([('id', '=', self.env.context.get('active_id'))], limit=1)
        name = current_invoice.documentnumber
        # if current_invoice.previous_abbr:
        #     name = current_invoice.documentnumber + chr(ord(current_invoice.previous_abbr) + 1)
        #     # current_invoice.previous_abbr = name
        # else:
        #     current_invoice.previous_abbr = 'A'
        #     name = current_invoice.documentnumber + 'A'
        if current_invoice:
            splited_invoice_dict = {
                'name': name,
                'splitted_date': current_invoice.invoice_date,
                'invoice_id': current_invoice.id,
                'partner_id': current_invoice.partner_id.id,
                'documentdate': current_invoice.documentdate,
                'documentnumber': current_invoice.documentnumber,
                'documenttypecode': current_invoice.documenttypecode,
                'supplytypecode': current_invoice.supplytypecode,
                'recipientlegalname': current_invoice.recipientlegalname,
                'recipienttradename': current_invoice.recipienttradename,
                'recipientgstin': current_invoice.recipientgstin,
                'placeofsupply': current_invoice.placeofsupply,
                'recipientaddress1': current_invoice.recipientaddress1,
                'recipientaddress2': current_invoice.recipientaddress2,
                'recipientplace': current_invoice.recipientplace,
                'recipientstatecode': current_invoice.recipientstatecode,
                'recipientpincode': current_invoice.recipientpincode,
                'slno': current_invoice.slno,
                'itemdescription': current_invoice.itemdescription,
                'istheitemagood': current_invoice.istheitemagood,
                'hsnorsaccode': current_invoice.hsnorsaccode,
                'quantity': current_invoice.quantity,
                'unitofmeasurement': current_invoice.unitofmeasurement,
                'itemprice': current_invoice.itemprice,
                'grossamount': current_invoice.grossamount,
                'itemdiscountamount': current_invoice.itemdiscountamount,
                'itemtaxablevalue': current_invoice.itemtaxablevalue,
                'gstrate': current_invoice.gstrate,
                'igstamount': current_invoice.igstamount,
                'csgtamount': current_invoice.csgtamount,
                'sgst_utgstamount': current_invoice.sgst_utgstamount,
                'compcessamountadvalorem': current_invoice.compcessamountadvalorem,
                'statecessamountadvalorem': current_invoice.statecessamountadvalorem,
                'otherchargesitemlevel': current_invoice.otherchargesitemlevel,
                'itemtotalamount': current_invoice.itemtotalamount,
                'totaltaxablevalue': current_invoice.totaltaxablevalue,
                'igstamounttotal': current_invoice.igstamounttotal,
                'cgstamounttotal': current_invoice.cgstamounttotal,
                'sgst_utgstamounttotal': current_invoice.sgst_utgstamounttotal,
                'compcessamounttotal': current_invoice.compcessamounttotal,
                'statecessamounttotal': current_invoice.statecessamounttotal,
                'otherchargeinvoicelevel': current_invoice.otherchargeinvoicelevel,
                'roundoffamount': current_invoice.roundoffamount,
                'totalinvoicevalueininr': current_invoice.totalinvoicevalueininr,
                'isreversechargeapplicable': current_invoice.isreversechargeapplicable,
                'igstactapplicability': current_invoice.igstactapplicability,
                'precedingdocumentnumber': current_invoice.precedingdocumentnumber,
                'precedingdocumentdate': current_invoice.precedingdocumentdate,
                'supplierlegalname': current_invoice.supplierlegalname,
                'gstinofsupplier': current_invoice.gstinofsupplier,
                'supplieraddress1': current_invoice.supplieraddress1,
                'supplierplace': current_invoice.supplierplace,
                'supplierstatecode': current_invoice.supplierstatecode,
                'supplierpincode': current_invoice.supplierpincode,
                'typeofexport': current_invoice.typeofexport,
                'shippingportcode': current_invoice.shippingportcode,
                'shippingbillnumber': current_invoice.shippingbillnumber,
                'shippingbilldate': current_invoice.shippingbilldate,
                'payeename': current_invoice.payeename,
                'payeebankaccountnumber': current_invoice.payeebankaccountnumber,
                'modeofpayment': current_invoice.modeofpayment,
                'bankbranchcode': current_invoice.bankbranchcode,
                'paymentterms': current_invoice.paymentterms,
                'paymentinstruction': current_invoice.paymentinstruction,
                'credittransferterms': current_invoice.credittransferterms,
                'directdebitterms': current_invoice.directdebitterms,
                'creditdays': current_invoice.creditdays,
                'shiptolegalname': current_invoice.shiptolegalname,
                'shiptogstin': current_invoice.shiptogstin,
                'shiptoaddress1': current_invoice.shiptoaddress1,
                'shiptoplace': current_invoice.shiptoplace,
                'shiptopincode': current_invoice.shiptopincode,
                'shiptostatecode': current_invoice.shiptostatecode,
                'dispatchfromname': current_invoice.dispatchfromname,
                'dispatchfromaddress1': current_invoice.dispatchfromaddress1,
                'dispatchfromplace': current_invoice.dispatchfromplace,
                'dispatchfromstatecode': current_invoice.dispatchfromstatecode,
                'dispatchfrompincode': current_invoice.dispatchfrompincode,
                'taxscheme': current_invoice.taxscheme,
                'transporterid': current_invoice.transporterid,
                'transmode': current_invoice.transmode,
                'transdistance': current_invoice.transdistance,
                'transportername': current_invoice.transportername,
                'transdocno': current_invoice.transdocno,
                'transdocdate': current_invoice.transdocdate,
                'vehicleno': current_invoice.vehicleno,
                'vehicletype': current_invoice.vehicletype,
                'receiptadvicereference': current_invoice.receiptadvicereference,
                'receiptadvicedate': current_invoice.receiptadvicedate,
                'tenderorlotreference': current_invoice.tenderorlotreference,
                'contractreference': current_invoice.contractreference,
                'externalreference': current_invoice.externalreference,
                'projectreference': current_invoice.projectreference,
                'poreferencenumber': current_invoice.poreferencenumber,
                'poreferencedate': current_invoice.poreferencedate,
                'additionalsupportingdocumentsurl': current_invoice.additionalsupportingdocumentsurl,
                'additionalinformation': current_invoice.additionalinformation,
                'documentperiodstartdate': current_invoice.documentperiodstartdate,
                'documentperiodenddate': current_invoice.documentperiodenddate,
                'additionalcurrencycode': current_invoice.additionalcurrencycode,
                'barcode': current_invoice.barcode,
                'freequantity': current_invoice.freequantity,
                'pretaxvalue': current_invoice.pretaxvalue,
                'compcessrateadvalorem': current_invoice.compcessrateadvalorem,
                'compcessamountnonadvalorem': current_invoice.compcessamountnonadvalorem,
                'statecessrateadvalorem': current_invoice.statecessrateadvalorem,
                'statecessamountnonadvalorem': current_invoice.statecessamountnonadvalorem,
                'purchaseorderlinereference': current_invoice.purchaseorderlinereference,
                'origincountrycode': current_invoice.origincountrycode,
                'uniqueserialnumber': current_invoice.uniqueserialnumber,
                'batchnumber': current_invoice.batchnumber,
                'batchexpirydate': current_invoice.batchexpirydate,
                'warrantydate': current_invoice.warrantydate,
                'attributename': current_invoice.attributename,
                'attributevalue': current_invoice.attributevalue,
                'countrycodeofexport': current_invoice.countrycodeofexport,
                'recipientphone': current_invoice.recipientphone,
                'recipientemailid': current_invoice.recipientemailid,
                'recipientaddress2': current_invoice.recipientaddress2,
                'totalinvoicevalueinfcnr': current_invoice.totalinvoicevalueinfcnr,
                'paidamount': current_invoice.paidamount,
                'amountdue': current_invoice.amountdue,
                'discountamountinvoicelevel': current_invoice.discountamountinvoicelevel,
                'tradenameofsupplier': current_invoice.tradenameofsupplier,
                'supplieraddress2': current_invoice.supplieraddress2,
                'supplierphone': current_invoice.supplierphone,
                'supplieremail': current_invoice.supplieremail,
                'shiptotradename': current_invoice.shiptotradename,
                'shiptoaddress2': current_invoice.shiptoaddress2,
                'dispatchfromaddress2': current_invoice.dispatchfromaddress2,
                'remarks': current_invoice.remarks,
                'exportdutyamount': current_invoice.exportdutyamount,
                'suppliercanoptrefund': current_invoice.suppliercanoptrefund,
                'ecomgstin': current_invoice.ecomgstin,
                'otherreference': current_invoice.otherreference,
                'buyerothcons' : current_invoice.buyerothcons,
                'cerno': current_invoice.cerno,
                'cinno': current_invoice.cinno,
                'panno': current_invoice.panno,
                'iecodeno': current_invoice.iecodeno,
                'lutno': current_invoice.lutno,
                'vesselflightno': current_invoice.vesselflightno,
                'portofloading': current_invoice.portofloading,
                'portofdischarge': current_invoice.portofdischarge,
                'countryoforigin': current_invoice.countryoforigin,
                'countryoffdest': current_invoice.countryoffdest,
                'termofdelpmnt': current_invoice.termofdelpmnt,
                'findest': current_invoice.findest,
                'noofpkgs': current_invoice.noofpkgs,
            }
            splited_invoice = self.env['split.initial.invoice'].create(splited_invoice_dict)
            move_lines = self.env['account.move.line'].search([('move_id', '=',self.env.context.get('active_id')),('exclude_from_invoice_tab','=',False),('splitted', '=', False)])
            for product in move_lines:
                product.splitted = True
                splited_invoice_line_dict = {
                    'move_line_id':product.id,
                    'product_id': product.product_id.id,
                    'label': product.name,
                    'quantity': product.quantity,
                    'price_unit': product.price_unit,
                    'subtotal': product.price_subtotal,
                    'split_invoice': splited_invoice.id,

                    'linenumber': product.linenumber,
                    'itemdescription': product.itemdescription,
                    'istheitemagood': product.istheitemagood,
                    'hsnorsaccode': product.hsnorsaccode,
                    'quantity': product.quantity,
                    'unitofmeasurement': product.unitofmeasurement,
                    'itemprice': product.itemprice,
                    'grossamount': product.grossamount,
                    'itemdiscountamount': product.itemdiscountamount,
                    'itemtaxablevalue': product.itemtaxablevalue,
                    'gstrate': product.gstrate,
                    'igstamount': product.igstamount,
                    'itemtotalamount': product.itemtotalamount,
                    'totaltaxablevalue': product.totaltaxablevalue,
                    'igstamounttotal': product.igstamounttotal,
                    'dispercent': product.dispercent,
                    'qtyinctn': product.qtyinctn,
                    'amtinusd': product.amtinusd,
                    'netamtinusdfob': product.netamtinusdfob,
                    'rateperkgusd': product.rateperkgusd,

                    'categorylvl1': product.categorylvl1,
                    'categorylvl2': product.categorylvl2,
                    'category': product.category,
                    'categorygrp': product.categorygrp,
                    'subgrp': product.subgrp,

                }
                self.env['split.initial.invoice.line'].create(splited_invoice_line_dict)

            current_invoice.splitted_invoices = [(4, splited_invoice.id)]

    def split_invoice(self):

        print("split invoiceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")


        current_invoice = self.env['account.move'].search([('id','=',self.env.context.get('active_id'))],limit=1)
        name = current_invoice.documentnumber
        # if current_invoice.previous_abbr:
        #     name = current_invoice.documentnumber + chr(ord(current_invoice.previous_abbr) + 1)
        #     # current_invoice.previous_abbr = name
        # else:
        #     current_invoice.previous_abbr = 'A'
        #     name = current_invoice.documentnumber + 'A'
        if current_invoice:
            splited_invoice_dict = {
                'name':name,
                'splitted_date':current_invoice.invoice_date,
                'invoice_id':current_invoice.id,
                'partner_id':current_invoice.partner_id.id,
                'documentdate': current_invoice.documentdate,
                'documentnumber':current_invoice.documentnumber ,
                'documenttypecode': current_invoice.documenttypecode,
                'supplytypecode': current_invoice.supplytypecode,
                'recipientlegalname': current_invoice.recipientlegalname,
                'recipienttradename': current_invoice.recipienttradename,
                'recipientgstin': current_invoice.recipientgstin,
                'placeofsupply': current_invoice.placeofsupply,
                'recipientaddress1': current_invoice.recipientaddress1,
                'recipientaddress2': current_invoice.recipientaddress2,
                'recipientplace': current_invoice.recipientplace,
                'recipientstatecode': current_invoice.recipientstatecode,
                'recipientpincode': current_invoice.recipientpincode,
                'slno': current_invoice.slno,
                'itemdescription': current_invoice.itemdescription,
                'istheitemagood': current_invoice.istheitemagood,
                'hsnorsaccode': current_invoice.hsnorsaccode,
                'quantity': current_invoice.quantity,
                'unitofmeasurement': current_invoice.unitofmeasurement,
                'itemprice': current_invoice.itemprice,
                'grossamount': current_invoice.grossamount,
                'itemdiscountamount': current_invoice.itemdiscountamount,
                'itemtaxablevalue': current_invoice.itemtaxablevalue,
                'gstrate': current_invoice.gstrate,
                'igstamount': current_invoice.igstamount,
                'csgtamount': current_invoice.csgtamount,
                'sgst_utgstamount': current_invoice.sgst_utgstamount,
                'compcessamountadvalorem': current_invoice.compcessamountadvalorem,
                'statecessamountadvalorem': current_invoice.statecessamountadvalorem,
                'otherchargesitemlevel': current_invoice.otherchargesitemlevel,
                'itemtotalamount': current_invoice.itemtotalamount,
                'totaltaxablevalue': current_invoice.totaltaxablevalue,
                'igstamounttotal': current_invoice.igstamounttotal,
                'cgstamounttotal': current_invoice.cgstamounttotal,
                'sgst_utgstamounttotal': current_invoice.sgst_utgstamounttotal,
                'compcessamounttotal': current_invoice.compcessamounttotal,
                'statecessamounttotal': current_invoice.statecessamounttotal,
                'otherchargeinvoicelevel': current_invoice.otherchargeinvoicelevel,
                'roundoffamount': current_invoice.roundoffamount,
                'totalinvoicevalueininr': current_invoice.totalinvoicevalueininr,
                'isreversechargeapplicable': current_invoice.isreversechargeapplicable,
                'igstactapplicability': current_invoice.igstactapplicability,
                'precedingdocumentnumber': current_invoice.precedingdocumentnumber,
                'precedingdocumentdate': current_invoice.precedingdocumentdate,
                'supplierlegalname': current_invoice.supplierlegalname,
                'gstinofsupplier': current_invoice.gstinofsupplier,
                'supplieraddress1': current_invoice.supplieraddress1,
                'supplierplace': current_invoice.supplierplace,
                'supplierstatecode': current_invoice.supplierstatecode,
                'supplierpincode': current_invoice.supplierpincode,
                'typeofexport': current_invoice.typeofexport,
                'shippingportcode': current_invoice.shippingportcode,
                'shippingbillnumber': current_invoice.shippingbillnumber,
                'shippingbilldate': current_invoice.shippingbilldate,
                'payeename': current_invoice.payeename,
                'payeebankaccountnumber': current_invoice.payeebankaccountnumber,
                'modeofpayment': current_invoice.modeofpayment,
                'bankbranchcode': current_invoice.bankbranchcode,
                'paymentterms': current_invoice.paymentterms,
                'paymentinstruction': current_invoice.paymentinstruction,
                'credittransferterms': current_invoice.credittransferterms,
                'directdebitterms': current_invoice.directdebitterms,
                'creditdays': current_invoice.creditdays,
                'shiptolegalname': current_invoice.shiptolegalname,
                'shiptogstin': current_invoice.shiptogstin,
                'shiptoaddress1': current_invoice.shiptoaddress1,
                'shiptoplace': current_invoice.shiptoplace,
                'shiptopincode': current_invoice.shiptopincode,
                'shiptostatecode': current_invoice.shiptostatecode,
                'dispatchfromname': current_invoice.dispatchfromname,
                'dispatchfromaddress1': current_invoice.dispatchfromaddress1,
                'dispatchfromplace': current_invoice.dispatchfromplace,
                'dispatchfromstatecode': current_invoice.dispatchfromstatecode,
                'dispatchfrompincode': current_invoice.dispatchfrompincode,
                'taxscheme': current_invoice.taxscheme,
                'transporterid': current_invoice.transporterid,
                'transmode': current_invoice.transmode,
                'transdistance': current_invoice.transdistance,
                'transportername': current_invoice.transportername,
                'transdocno': current_invoice.transdocno,
                'transdocdate': current_invoice.transdocdate,
                'vehicleno': current_invoice.vehicleno,
                'vehicletype': current_invoice.vehicletype,
                'receiptadvicereference': current_invoice.receiptadvicereference,
                'receiptadvicedate': current_invoice.receiptadvicedate,
                'tenderorlotreference': current_invoice.tenderorlotreference,
                'contractreference': current_invoice.contractreference,
                'externalreference': current_invoice.externalreference,
                'projectreference': current_invoice.projectreference,
                'poreferencenumber': current_invoice.poreferencenumber,
                'poreferencedate': current_invoice.poreferencedate,
                'additionalsupportingdocumentsurl': current_invoice.additionalsupportingdocumentsurl,
                'additionalinformation': current_invoice.additionalinformation,
                'documentperiodstartdate': current_invoice.documentperiodstartdate,
                'documentperiodenddate': current_invoice.documentperiodenddate,
                'additionalcurrencycode': current_invoice.additionalcurrencycode,
                'barcode': current_invoice.barcode,
                'freequantity': current_invoice.freequantity,
                'pretaxvalue': current_invoice.pretaxvalue,
                'compcessrateadvalorem': current_invoice.compcessrateadvalorem,
                'compcessamountnonadvalorem': current_invoice.compcessamountnonadvalorem,
                'statecessrateadvalorem': current_invoice.statecessrateadvalorem,
                'statecessamountnonadvalorem': current_invoice.statecessamountnonadvalorem,
                'purchaseorderlinereference': current_invoice.purchaseorderlinereference,
                'origincountrycode': current_invoice.origincountrycode,
                'uniqueserialnumber': current_invoice.uniqueserialnumber,
                'batchnumber': current_invoice.batchnumber,
                'batchexpirydate': current_invoice.batchexpirydate,
                'warrantydate': current_invoice.warrantydate,
                'attributename': current_invoice.attributename,
                'attributevalue': current_invoice.attributevalue,
                'countrycodeofexport': current_invoice.countrycodeofexport,
                'recipientphone': current_invoice.recipientphone,
                'recipientemailid': current_invoice.recipientemailid,
                'recipientaddress2': current_invoice.recipientaddress2,
                'totalinvoicevalueinfcnr': current_invoice.totalinvoicevalueinfcnr,
                'paidamount': current_invoice.paidamount,
                'amountdue': current_invoice.amountdue,
                'discountamountinvoicelevel': current_invoice.discountamountinvoicelevel,
                'tradenameofsupplier': current_invoice.tradenameofsupplier,
                'supplieraddress2': current_invoice.supplieraddress2,
                'supplierphone': current_invoice.supplierphone,
                'supplieremail': current_invoice.supplieremail,
                'shiptotradename': current_invoice.shiptotradename,
                 'shiptoaddress2': current_invoice.shiptoaddress2,
                'dispatchfromaddress2': current_invoice.dispatchfromaddress2,
                'remarks': current_invoice.remarks,
                'exportdutyamount': current_invoice.exportdutyamount,
                'suppliercanoptrefund': current_invoice.suppliercanoptrefund,
                'ecomgstin': current_invoice.ecomgstin,
                'otherreference': current_invoice.otherreference,
                'buyerothcons' : current_invoice.buyerothcons,
                'cerno': current_invoice.cerno,
                'cinno': current_invoice.cinno,
                'panno': current_invoice.panno,
                'iecodeno': current_invoice.iecodeno,
                'lutno': current_invoice.lutno,
                'vesselflightno': current_invoice.vesselflightno,
                'portofloading': current_invoice.portofloading,
                'portofdischarge': current_invoice.portofdischarge,
                'countryoforigin': current_invoice.countryoforigin,
                'countryoffdest': current_invoice.countryoffdest,
                'termofdelpmnt': current_invoice.termofdelpmnt,
                'findest': current_invoice.findest,
                'noofpkgs': current_invoice.noofpkgs,
                }
            splited_invoice = self.env['split.initial.invoice'].create(splited_invoice_dict)

            for product in self.order_line:
                product.splitted =True
                splited_invoice_line_dict = {
                    'move_line_id':product.id,
                    'product_id':product.product_id.id,
                    'label':product.name,
                    'quantity':product.quantity,
                    'price_unit':product.price_unit,
                    'subtotal':product.price_subtotal,
                    'split_invoice':splited_invoice.id,

                    'linenumber': product.linenumber,
                    'itemdescription': product.itemdescription,
                    'istheitemagood': product.istheitemagood,
                    'hsnorsaccode': product.hsnorsaccode,
                    'quantity': product.quantity,
                    'unitofmeasurement': product.unitofmeasurement,
                    'itemprice': product.itemprice,
                    'grossamount': product.grossamount,
                    'itemdiscountamount': product.itemdiscountamount,
                    'itemtaxablevalue': product.itemtaxablevalue,
                    'gstrate':product.gstrate,
                    'igstamount': product.igstamount,
                    'itemtotalamount': product.itemtotalamount,
                    'totaltaxablevalue':product.totaltaxablevalue,
                    'igstamounttotal':product.igstamounttotal,
                    'dispercent' : product.dispercent,
                    'qtyinctn' : product.qtyinctn,
                    'amtinusd' : product.amtinusd,
                    'netamtinusdfob' : product.netamtinusdfob,
                    'rateperkgusd' : product.rateperkgusd,

                    'categorylvl1' : product.categorylvl1,
                    'categorylvl2' : product.categorylvl2,
                    'category' : product.category,
                    'categorygrp' : product.categorygrp,
                    'subgrp' : product.subgrp,



                }
                self.env['split.initial.invoice.line'].create(splited_invoice_line_dict)

            current_invoice.splitted_invoices = [(4,splited_invoice.id)]

