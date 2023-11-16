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
    invoice_upload = fields.Binary("Upload Invoice")

    asn_line_ids = fields.One2many('asn.lines', 'asn_lines', string='ASN line')

    @api.onchange('po_no')
    def _onchange_partners(self):
        for datas in self:
            if self.po_no:
                self.date_approve = self.po_no.date_approve
                self.purchase_representative = self.po_no.user_id.id
                transfers = self.env['stock.picking'].sudo().search(
                    [('origin', '=', self.po_no.name), ('state', '=', 'assigned')])
                for transfer in transfers:
                    self.transfer = transfer.id
                    line = []
                    for stck_lines in transfer.move_ids_without_package:
                        val = {
                            'product_id': stck_lines.product_id.id,
                            'quantity': stck_lines.product_uom_qty,
                        }
                        line.append((0, 0, val))
                        print(line)
                    datas.asn_line_ids = line

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

    product_id = fields.Many2one('product.product', string='products')
    quantity = fields.Float(string='Demand Quantity')
    provide_qty = fields.Float(string='Quantity Suppliable')
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
