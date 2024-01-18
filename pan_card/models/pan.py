from odoo import models, fields, api



class ManufactureOrder(models.Model):
    _inherit = 'res.partner'

    pan = fields.Char("Pan Number")

    # _sql_constraints = [
    #     ('unique_pan', 'unique (pan)', 'This Pan already exists')
    # ]



class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    branch_code = fields.Char('Branch Code')
    division = fields.Char('Division')
    sub_division = fields.Char('Sub Divisosn')
    region = fields.Char('Region')
    main = fields.Char('Main/Child')
    pan = fields.Char('PAN No')


class BankDetailsInh(models.Model):
    _inherit = 'res.partner.bank'

    ifsc = fields.Char("IFSC Code")
    