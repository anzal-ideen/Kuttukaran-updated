from odoo import models, fields, api, _
from odoo.exceptions import UserError







class StockDeliveryDate(models.Model):
    _inherit = 'stock.picking'

    delivery_commitment = fields.Datetime(string="Delivery Commitment Date", store=True)
    asm_date = fields.Datetime(string="Advanced Shipment Date", store=True)


    def view_asn(self):
        print("ASNNN")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Aavanced Shipment Notice',
            'view_mode': 'tree,form',
            'res_model': 'advanced.shipment.notice',
            'domain': [('transfer', '=', self.id)],
            'target': 'current'
        }




class PurchaseVendorUser(models.Model):
    _inherit = 'purchase.order'

    vendor_user_id = fields.Many2one('res.users', string='Vendor User', compute='_compute_vendor_user_id',
        store=True)
    delivery_commitment = fields.Boolean("Delivery Commited")
    asm_date = fields.Boolean("ASN Date")
    menu_1 = fields.Boolean("Second menu")

    @api.model
    def create(self, values):
        if self.env.user.has_group('vendor_portal.group_vendor_portal_user'):
            raise UserError(_('You are not allowed to create/ edit PO. Please contact Administrator.'))

        return super(PurchaseVendorUser, self).create(values)

    def unlink(self):
        if self.env.user.has_group('vendor_portal.group_vendor_portal_user'):
            raise UserError(_('You are not allowed to delete this PO. Please contact Administrator.'))
        else:
            return super(PurchaseVendorUser, self).unlink()

    def toggle_active(self):
        for order in self:
            if self.env.user.has_group('vendor_portal.group_vendor_portal_user'):
                raise UserError(_('You can not archive/ unarchive this PO. Please contact Administrator.'))
            return super(PurchaseVendorUser, order).toggle_active()

    def action_rfq_send(self):
        print("hiiiiiiiiiiiiiiiiii")
        if self.env.user.has_group('vendor_portal.group_vendor_portal_user'):
            raise UserError(_('You are not allowed to delete this PO. Please contact Administrator.'))
        else:
            return super(PurchaseVendorUser, self).action_rfq_send()






    def button_delivery_commit(self):
        print("helloooo")
        action = self.env["ir.actions.actions"]._for_xml_id('vendor_po.update_commitment_date_action')
        action['context'] = {'default_purchase_id': self.id}

        # action = self.env.ref(
        #     'sale_confirmation_date.update_confirmation_date_action').read()[0]
        return action

    def button_adv_shipment_date(self):
        print("hiiiiiiiiiiiii")

        transfer_lines =[]
        for transfer in self.picking_ids:
            print(transfer)
            if transfer.state == 'assigned':
                for lines in transfer.move_ids_without_package:
                    print(lines)
                    transfer_lines.append((0, 0, {
                        'product_id': lines.product_id.id,
                        'quantity': lines.product_uom_qty,
                        # 'p_line_lot': lines.lot_name
                    }))
                    print(transfer_lines)

                vals={

                    'partner_id': self.partner_id.id,
                    'purchase_representative': self.user_id.id,
                    'po_no': self.id,
                    'transfer': transfer.id,
                    'asn_line_ids': transfer_lines,
                    'date_approve': self.date_approve,

                }
                asn = self.env['advanced.shipment.notice'].search([('transfer', '=', transfer.id,)], limit=1) or False
                if asn:
                    raise UserError(
                f"Advanced Shipment Notice for {transfer.name} is already created.")


                new_package = self.env['advanced.shipment.notice'].create(vals)
                self.env.cr.commit()
                new_pack = self.env['advanced.shipment.notice'].search([('id', '=', new_package.id)], limit=1) or False
                context = dict(self.env.context)
                context['form_view_initial_mode'] = 'edit'
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Advanced Shipment Notice',
                    'res_model': 'advanced.shipment.notice',
                    'view_mode': 'form',
                    'res_id': new_package.id,
                    'target': 'current',
                    'context': {
                        'form_view_initial_mode': 'edit',
                    },

                }



        # action = self.env["ir.actions.actions"]._for_xml_id('vendor_po.update_advanced_shipmnt_date_action')
        # action['context'] = {'default_purchase_id': self.id}
        #
        # return action

    @api.depends('partner_id')
    def _compute_vendor_user_id(self):
        # for user in self:
        if self.partner_id:
            vendor_user_id = self.env['res.users'].sudo().search([
            ('partner_id', '=', self.partner_id.id)])
            print(vendor_user_id.name)
            print(vendor_user_id.id)
            if vendor_user_id:
                self.vendor_user_id = vendor_user_id.id
            else:
                self.vendor_user_id = False
        else:
            self.vendor_user_id = False