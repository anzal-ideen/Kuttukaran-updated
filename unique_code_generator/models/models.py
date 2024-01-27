from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'


    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Supplier'),
    ], 'Partner Type')

    customer = fields.Boolean(compute='_compute_customer', inverse='_inverse_customer', store=True,
                              string="Is a Customer")
    supplier = fields.Boolean(compute='_compute_supplier', inverse='_inverse_supplier', store=True,
                              string="Is a Supplier")

    vendor_code = fields.Char("Code",compute='compute_vendor_code')

    @api.depends('partner_type')
    def compute_vendor_code(self):
        for record in self:
            if not record.vendor_code:
                if record.partner_type == 'vendor':
                    record.vendor_code = self.env['ir.sequence'].next_by_code('vendor.code')
                if record.partner_type == 'customer':
                    record.vendor_code = self.env['ir.sequence'].next_by_code('customer.code')

    @api.depends('customer_rank')
    def _compute_customer(self):
        for partner in self:
            partner.customer = True if partner.customer_rank > 0 else False

    def _inverse_customer(self):
        for partner in self:
            partner.customer_rank = 1 if partner.customer else 0
            partner.supplier = not partner.customer

    @api.depends('supplier_rank')
    def _compute_supplier(self):
        for partner in self:
            partner.supplier = True if partner.supplier_rank > 0 else False

    def _inverse_supplier(self):
        for partner in self:
            partner.supplier_rank = 1 if partner.supplier else 0
            partner.customer = not partner.supplier



    # @api.onchange('partner_type', 'supplier', 'customer')
    # def set_partner_ref(self):
    #     for record in self:
    #         if not record.ref:
    #             if record.partner_type == 'domestic' and record.supplier is True:
    #                 record.ref = self.env['ir.sequence'].next_by_code('domestic.vendor.code')
    #             if record.partner_type == 'domestic' and record.customer is True:
    #                 record.ref = self.env['ir.sequence'].next_by_code('domestic.customer.code')
    #             if record.partner_type == 'exp/imp' and record.supplier is True:
    #                 record.ref = self.env['ir.sequence'].next_by_code('export.import.vendor.code')
    #             if record.partner_type == 'exp/imp' and record.customer is True:
    #                 record.ref = self.env['ir.sequence'].next_by_code('export.import.customer.code')
    #             if record.partner_type == 'customer/supplier' and (record.supplier or record.customer):
    #                 record.ref = self.env['ir.sequence'].next_by_code('vendor.customer.code')
