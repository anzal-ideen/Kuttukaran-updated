from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AsNotice(models.Model):
    _name = 'advanced.shipment.notice'

    name = fields.Char(string='Number', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Partner', default=lambda self: self.env.user.partner_id,
                                 readonly=True, store=True, force_save=1)
    purchase_representative = fields.Many2one('res.users', "Purchase Representative", store=True, force_save=1)
    po_no = fields.Many2one('purchase.order', "Purchase Order",
                            domain="[('partner_id', '=', partner_id), ('state','=','purchase')]")
    transfer = fields.Many2one('stock.picking', "Transfer No", store=True, force_save=1
                               )
    date_approve = fields.Datetime("PO Confirmation Date", store=True, force_save=1)
    asn_date = fields.Datetime("Adavanced Shipment Date")
    state = fields.Selection([("draft", "Draft"), ("submit", "Submitted")], string="Status", default="draft")
    invoice_no = fields.Char("Invoice Number")
    lr = fields.Char("LR Number")
    lr_date = fields.Date("LR Date")
    carrier = fields.Char("Carrier No")
    eway = fields.Char("E-way Bill No")
    utr = fields.Char("Payment UTR No")
    invoice_upload = fields.Binary("Upload Invoice")
    workorder_upload = fields.Binary("Work Order")
    total_amount = fields.Float("Total" , readonly=1,store=True)
    un_taxed_amount = fields.Float("Untaxed Total" , readonly=1,store=True)
    total_amount_supplied = fields.Float("Total Amount", compute='compute_total_supply_amount',store=True)


    asn_line_ids = fields.One2many('asn.lines', 'asn_lines', string='ASN line')

    @api.depends('asn_line_ids.provide_qty', 'asn_line_ids.unit_price')
    def compute_total_supply_amount(self):
        for total in self:
            total_amount = 0.0
            for line_total in total.asn_line_ids:
                if line_total.provide_qty and line_total.unit_price:
                    total_amount += line_total.provide_qty * line_total.unit_price
            total.total_amount_supplied = total_amount


    @api.onchange('po_no')
    def _onchange_partners(self):
        for datas in self:
            if datas.po_no:
                print(datas.po_no.order_line)
                datas.asn_line_ids = [(5, 0, 0)]
                datas.date_approve = datas.po_no.date_approve
                datas.purchase_representative = datas.po_no.user_id.id
                line = []
                for po_lines in datas.po_no.order_line:
                    print(datas.po_no.name)
                    print(po_lines.product_qty)
                    print(po_lines.price_unit)
                    print(po_lines.taxes_id)
                    val = {
                        'product_id': po_lines.product_id.id,
                        'quantity': po_lines.product_uom_qty,
                        'unit_price': po_lines.price_unit,
                        'delivered': po_lines.qty_received,
                        'tax': po_lines.taxes_id.id,
                        'sub_total': po_lines.price_subtotal,
                    }
                    line.append((0, 0, val))
                datas.total_amount = datas.po_no.amount_total
                datas.un_taxed_amount = datas.po_no.amount_untaxed

                    # print(line)
                datas.asn_line_ids = line

                transfers = self.env['stock.picking'].sudo().search(
                    [('origin', '=', self.po_no.name), ('state', '=', 'assigned')])
                for transfer in transfers:
                    self.transfer = transfer.id
                    line = []
                    # for stck_lines in transfer.move_ids_without_package:
                    #     val = {
                    #         'product_id': stck_lines.product_id.id,
                    #         'quantity': stck_lines.product_uom_qty,
                    #     }
                    #     line.append((0, 0, val))
                    #     print(line)
                    # datas.asn_line_ids = line

    def action_submit(self):
        print("helloooo")
        if self.invoice_upload:
            if self.asn_date:
                self.state='submit'
                transfer = self.env['stock.picking'].search([('id', '=', self.transfer.id)])
                for tr in transfer:
                    tr.asm_date = self.asn_date
            else:
                raise UserError("Please enter Advanced Shipment Date")
        else:
            raise UserError("Please Upload Invoice")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('advanced.shipment.notice') or _('New')
        res = super(AsNotice, self).create(vals)
        return res


class AsnLiness(models.Model):
    _name = "asn.lines"

    product_id = fields.Many2one('product.product', string='products',readonly=1,store=True)
    quantity = fields.Float(string='Demand Quantity',readonly=1,store=True)
    provide_qty = fields.Float(string='Quantity Suppliable')
    delivered = fields.Float(string='Delivered',readonly=1,store=True)
    unit_price = fields.Float(string='Unit Price',readonly=1,store=True)
    tax = fields.Many2one('account.tax',"Taxes",readonly=1,store=True)
    sub_total = fields.Char("Sub Total",readonly=1,store=True)
    remark = fields.Char(string="Remark")


    asn_lines = fields.Many2one('advanced.shipment.notice', string='Params')





class InvoicePaymentInherit(models.Model):
    _inherit = 'account.move'

    def action_register_payment(self):
        result = super(InvoicePaymentInherit, self).action_register_payment()
        if self.move_type=='in_invoice':
            purchase_order_id = self.invoice_line_ids.mapped('purchase_line_id').order_id
            print(purchase_order_id.name)
            purchase_id = self.env['purchase.order'].search([('id', '=',purchase_order_id.id)])
            if purchase_id:
                for purchase in purchase_id:
                    if purchase.picking_ids:
                        for picking in purchase.picking_ids:
                            print(picking.name)
                            asn_details = self.env['advanced.shipment.notice'].search([('transfer', '=',picking.id)])
                            if asn_details:
                                print(asn_details)
                                if asn_details.invoice_upload:
                                    print("passs")
                                    return result
                                else:
                                    raise UserError("Please ask vendor to upload Invoice to ASN.")
                            else:
                                return result
                else:
                    return result
            else:
                return result
        else:
            return result



# class ResCompanyInherit(models.Model):
#     _inherit = 'res.company'
#
#     branch_code = fields.Char('Branch Code')
