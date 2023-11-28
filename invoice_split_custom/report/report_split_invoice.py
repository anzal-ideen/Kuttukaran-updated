# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, float_compare

import pytz

class ReportSplitInvoices(models.AbstractModel):
    _name = 'report.invoice_split_custom.report_invoice_split_custom'

    def get_products(self, docs):
        print("get producst")
        """input : starting date, location and category
          output: a dictionary with all the products and their stock for that currespnding intervals"""

        products = {'product1':'p1','product2':'p2'}

        return products


    @api.model
    def _get_report_values(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
                we pass the objects in the docargs dictionary"""

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docs =self.env['account.move'].search([],limit=1)
        print(docs)
        products = self.get_products(docs)


        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'products': products,
        }


