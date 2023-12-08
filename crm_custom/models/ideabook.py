from odoo import api, fields, models, _


class IdeaBook(models.Model):
    _name = "ideabook"
    _description = "ideabook"

    name = fields.Char(string="Sequence Number", default=lambda self: _('New'),
                       readonly=True)
    customer = fields.Many2one('res.partner', string="Customer")
    date = fields.Date(string="Date")
    ideabook_line_ids = fields.One2many('ideabook.line', 'ideabook_id',
                                               string='Ideabook Lines', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('ideabook') or _('New')
        res = super(IdeaBook, self).create(vals)
        return res


class IdeaBookLine(models.Model):
    _name = "ideabook.line"
    _description = "ideabook Line"

    number = fields.Integer(string="No")
    description = fields.Char(string="Description")
    image = fields.Char(string="Image")
    ideabook_id = fields.Many2one('ideabook', string='Ideabook', tracking=True)
