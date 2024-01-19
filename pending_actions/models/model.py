from datetime import datetime
from datetime import date
from odoo import api, fields, models, _ , tools
from odoo.exceptions import ValidationError, MissingError, UserError


class PendingActions(models.Model):
    _name = "pending.actions"
    # _auto = False
    _description = "Pending Actions"

    date = fields.Date("Date")
    name = fields.Char("Name")
    status = fields.Selection(
        selection=[('open', 'Open'), ('closed', 'Closed')],
        string='Status',
        default='open',
        tracking=True
    )
    model = fields.Many2one("ir.model","Action Type")
    record = fields.Integer("Record ID")
    record_line = fields.Integer("Line Record")
    approve_users = fields.Many2many(
        'res.users',
        'rel_pending_approvers',
        'pending_id',
        'pending_users',
        string='Approve Users',
    )



    def open_record(self):
        # model = self.model.model
        models = self.env['ir.model'].sudo().search([('id', '=',self.model.id)],limit=1)
        print(models)
        record = self.env[models.model].sudo().search([('id', '=', self.record)],limit=1)

        if record:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Record',
                'view_mode': 'form',
                'res_model': models.model,
                # 'domain': [('id', '=', self.record)],
                'target': 'current',
                'res_id': record.id,
            }

        else:
            raise UserError("No Document Found")





    # @api.model_create_single
    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'pending_actions')
    #     self._cr.execute("""
    #         CREATE OR REPLACE VIEW pending_actions AS (
    #             SELECT row_number() over() AS id,
    #                 req.name AS name,
    #                 req.requested_date AS date,
    #                 req.status AS status
    #             FROM
    #                 purchase_management_system AS req
    #         )
    #     """)
