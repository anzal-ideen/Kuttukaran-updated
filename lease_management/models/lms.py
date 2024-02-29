from datetime import datetime , timedelta
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError, UserError
from odoo.tools.safe_eval import json


class ProductLease(models.Model):
    _name = "product.lease"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Lease Request"

    name = fields.Char(string="Request No", readonly=True, required=True, copy=False, default='New')
    requested_date = fields.Datetime(string="Date", default=datetime.today(), readonly=True)
    product_id = fields.Many2one('product.template',string="Product")
    vendor_id = fields.Many2one('res.partner',string="Vendor")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'Requested By', default=lambda self: self.env.user, readonly=True)

    product_uom = fields.Many2one("uom.uom", "UOM", related="product_id.uom_id")

    auto_po = fields.Boolean("Auto Generate PO")
    auto_invoice = fields.Boolean("Auto Generate Invoice")
    with_gst = fields.Boolean("With Tax")
    tax = fields.Many2one("account.tax","Tax")
    upload_po = fields.Binary("Upload Invoice")


    state = fields.Selection(
        selection=[('draft', 'Draft'), ('request', 'Requested'), ('approve', 'Approved'),
                   ('reject', 'Rejected'),('expire', 'Expired')],
        string='State',
        default='draft',
        required=True
    )
    approve_line = fields.One2many('lease.approve.line',
                                   'approve_lease_id',
                                   string='Lease Approve Line',
                                   tracking=True)

    reccuring_line = fields.One2many('lease.recurring.po',
                                   'recurring_lease_id',
                                   string='Lease Recurring Line',
                                   tracking=True)



    approve_users = fields.Many2many(
        'res.users',
        'rel_lease_apprvers',
        'lease_id',
        'users',
        string='Approve Users',
    )
    approved_users = fields.Many2many(
        'res.users',
        'approved_lease_relation',
        'lease_apprved',
        'user_id',
        string='Approved Users',
    )

    next_approve_user = fields.Many2many(
        'res.users',
        'next_aprved_lease',
        'next_lease',
        'users_id',
        string='Next Approver',)

    is_an_approver = fields.Boolean("Approver",compute='compute_is_an_approver')
    user_approved = fields.Boolean("Approved",compute='compute_approved_user')
    compute_state = fields.Boolean("State",compute='compute_states')
    product_request_id = fields.Many2one("product.request","Request")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    qty = fields.Float("Quantity")
    price = fields.Float("Unit Price")
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    department_id = fields.Many2one('hr.department', string="Department")
    expense_type = fields.Selection([('cap', 'CapEx'), ('op', 'OpEx')], string='Expense Type', tracking=True)
    location = fields.Char(string='Location', tracking=True)
    address1 = fields.Char(string='Address 1', tracking=True)
    address2 = fields.Char(string='Address 2', tracking=True)
    city = fields.Char(string='City', tracking=True)
    state_name = fields.Char(string='State', tracking=True)
    security = fields.Float(string='Security Deposit', tracking=True)
    terms = fields.Text("Terms & Conditions")
    # total_rent = fields.Float(string='Total Rent', tracking=True , compute="compute_total_rent")
    total = fields.Float(string="Total Amount", compute="compute_total_amount",tracking=True)

    increment_method = fields.Selection([
        ('year', 'Yearly'),
        ('half', 'Semi Annual'),
        ('quarter', 'Quarterly'),
        ('custom', 'Custom Date'),
    ], 'Increment Method')

    increment_amount = fields.Selection([
        ('total', 'Total'),
        ('custom', 'Custom Amount'),
    ], 'Increment Based On')

    increment_by = fields.Selection([
        ('amount', 'Amount'),
        ('percent', '%'),
    ], 'Increment By')
    inc_date = fields.Date("Date", store = True)
    inc_value = fields.Float("Value" ,store = True)
    inc_amount = fields.Float("Rate")
    total_increment_value = fields.Float("Amount Incremented", compute='compute_total_increment')
    is_increment = fields.Boolean("Increment")
    amount_payable = fields.Float("Total Amount Payable ")

    ############## Not in Use #############

    bill_to = fields.Many2one('res.partner', "Bill To")
    ship_to = fields.Many2one('res.partner', "Ship To")
    expense_type = fields.Selection([('cap', 'CapEx'), ('op', 'OpEx')], string='Expense Type', tracking=True)
    product_lines = fields.One2many('lease.product.line',
                                    'lease_id',
                                    string='Product Lease Line',
                                    tracking=True)

    exp_category = fields.Many2one('expense.category','Expense Category', required=True)

    exp_category_domain = fields.Char(
        compute="_compute_exp_category_domain",
        readonly=True,
        store=False,
    )


    @api.depends('expense_type')
    def _compute_exp_category_domain(self):
        for rec in self:
            category_domain = []
            if rec.expense_type:
                categories = self.env['expense.category'].sudo().search([
                    ('exp_type', '=', rec.expense_type)
                ])
                if categories:
                    expense_types = categories.mapped('exp_type')
                    if expense_types:
                        category_domain = [('exp_type', '=', expense_types)]

            rec.exp_category_domain = json.dumps(category_domain)

    @api.depends('inc_amount', 'inc_value', 'increment_by')
    def compute_total_increment(self):
        for record in self:
            if record.inc_value and record.inc_amount and record.increment_by:
                if record.increment_by == 'amount':
                    record.total_increment_value = record.inc_amount + record.inc_value
                elif record.increment_by == 'percent':
                    percentage = record.inc_amount / 100
                    record.total_increment_value = record.inc_value + (record.inc_value * percentage)

                else:
                    record.total_increment_value = 0
            else:
                record.total_increment_value = 0


    def auto_lease_check(self):
        current_date = date.today()
        leases = self.env['product.lease'].search([('state', '=', 'approve')])
        for rec in leases:
            if not rec.amount_payable:
                rec.amount_payable = rec.total
            if rec.is_increment:
                if rec.inc_date and current_date == rec.inc_date:
                    if rec.increment_method == 'year':
                        rec.inc_date = rec.inc_date + timedelta(days=365)
                    elif rec.increment_method == 'half':
                        rec.inc_date = rec.inc_date + timedelta(days=182)
                    elif rec.increment_method == 'quarter':
                        rec.inc_date = rec.inc_date + timedelta(days=90)
                    elif rec.increment_method == 'custom':
                        rec.inc_date = rec.inc_date
                    if rec.increment_by == 'amount':
                        rec.amount_payable = rec.amount_payable + rec.inc_amount  # Increment by inc_amount
                        print("vghvvvvvvvvvvv",rec.amount_payable)
                    else:
                        percentage = rec.inc_amount / 100
                        rec.amount_payable = rec.amount_payable + (rec.amount_payable * percentage)
                        print(rec.amount_payable)

    # @api.onchange('total_increment_value')
    # def onchange_increment_amount(self):
    #     print("total onchange")
    #     if self.total_increment_value:
    #         self.amount_payable = self.total_increment_value
    #     else:
    #         pass

    @api.constrains('inc_value')
    def _constrains_inc_value(self):
        for record in self:
            if record.inc_value and record.inc_value < record.total:
                raise ValidationError("The increment value must be greater than or equal to the total value.")

    @api.constrains('inc_date', 'end_date')
    def _constrains_inc_date(self):
        for record in self:
            if record.inc_date and record.end_date:
                if record.inc_date > record.end_date:
                    raise ValidationError("The increment date must be less than or equal to the end date.")


    @api.onchange('start_date','increment_method')
    def onchange_increment_method(self):
        if self.start_date and self.increment_method == 'year':
            self.inc_date = self.start_date + timedelta(days=365)
        if self.start_date and self.increment_method == 'half':
            self.inc_date = self.start_date + timedelta(days=182)
        if self.start_date and self.increment_method == 'quarter':
            self.inc_date = self.start_date + timedelta(days=90)
        if self.start_date and self.increment_method == 'custom':
            self.inc_date = ""

    @api.onchange('increment_amount','total','qty','price')
    def onchange_increment_amount(self):
        print("kkk")
        if self.increment_amount == 'total':
            self.inc_value = self.total




    def _compute_attachment_number(self):
        domain = [('res_model', '=', 'product.lease'), ('res_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)




    def action_generate_po(self):
        print("hhhhhh")
        print(self._name)
        today = date.today()
        products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)],
                                                      limit=1)
        # print(products)
        for product in products:
            price_unit = 0.0
            if today >= self.inc_date:
                price_unit = self.amount_payable/self.qty
            else:
                price_unit = self.price            # print(product)
            order_line = [(0, 0, {
                'display_type': False,
                'name': products.name or '',
                'product_id': products.id,
                'price_unit': price_unit,
                'product_qty': self.qty,
                'product_uom': self.product_id.uom_po_id.id,
            })]
            # print(order_line)
            purchase_order = self.env['purchase.order'].create({
                'partner_id': self.vendor_id.id,
                'order_line': order_line,
                'company_id': self.company_id.id,
                'is_auto_po': True,
                'expense_type': self.expense_type or '',
                'exp_category': self.exp_category.id,
                'department_id': self.department_id.id or '',
                'bill_to': self.product_request_id.bill_to.id or self.company_id.id,
                'ship_to': self.product_request_id.ship_to.id or self.company_id.id,
                'location': self.product_request_id.bill_to.id or self.company_id.id,
            })
            self.env.cr.commit()
            if self.auto_invoice == True:
                purchase_order.button_confirm()
                for lines in purchase_order.order_line:
                    lines.qty_received = lines.product_qty
                purchase_order.action_create_invoice()

            po_vals = {
                'po': purchase_order.id,
                'date': fields.Date.today(),
                'status': purchase_order.state,
                'recurring_lease_id': self.id
            }

            po_create = self.env['lease.recurring.po'].create(
                po_vals
            )
            self.env.cr.commit()



    def action_open_attachments(self):
        print("kkkkkkkk")
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'product.lease'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'product.lease', 'default_res_id': self.id}
        return res




    # @api.depends('approved_users')
    # def compute_user_approved(self):
    #     for users in self.approved_users:
    #         if users in
    @api.onchange('state')
    def _onchange_state(self):
        for rec in self:
            print(rec)
        # if self.state == 'done':


    def check_expiration(self):
        today = date.today()
        lease = self.env['product.lease'].search([])
        for rec in lease:
            print(rec.end_date)
            if rec.end_date and today >= rec.end_date:
                rec.state = 'expire'

    def generate_auto_po(self):
        current_date = date.today()
        lease_status = self.env['product.lease'].search([('state', '=', 'approve'), ('end_date', '>=', current_date)
                        ,('auto_po','=',True)])
        print("heelllll")
        order_line = []

        for lease in lease_status:

            print(lease.product_request_id.name)
            products = self.env['product.product'].search([('product_tmpl_id', '=', lease.product_id.id)],
                                                          limit=1)
            # print(products)
            price_unit = 0.0
            if current_date >= lease.inc_date:
                price_unit = lease.amount_payable / lease.qty
            else:
                price_unit = lease.price  # print(product)
            for product in products:
                # print(product)
                order_line = [(0, 0, {
                    'display_type': False,
                    'name': products.name or '',
                    'product_id': products.id,
                    'price_unit': price_unit,
                    'product_qty': lease.qty,
                    'product_uom': lease.product_id.uom_po_id.id,
                })]
                # print(order_line)
                purchase_order = self.env['purchase.order'].create({
                    'partner_id': lease.vendor_id.id,
                    'order_line': order_line,
                    'company_id': lease.company_id.id,
                    'is_auto_po': True,
                    'expense_type': lease.expense_type or '',
                    'exp_category': lease.exp_category.id,
                    'department_id': lease.department_id.id or '',
                    'bill_to': lease.product_request_id.bill_to.id or lease.company_id.id,
                    'ship_to': lease.product_request_id.ship_to.id or lease.company_id.id,
                    'location': lease.product_request_id.bill_to.id or lease.company_id.id,
                })
                self.env.cr.commit()

                if lease.auto_invoice == True:
                    purchase_order.button_confirm()
                    for lines in purchase_order.order_line:
                        lines.qty_received = lines.product_qty
                    purchase_order.action_create_invoice()

                po_vals={
                    'po': purchase_order.id,
                    'date':  fields.Date.today(),
                    'status': purchase_order.state,
                    'recurring_lease_id':lease.id
                }

                po_create = self.env['lease.recurring.po'].create(
                    po_vals
                )
                self.env.cr.commit()



    @api.depends('state')
    def compute_states(self):
        if self.state == 'approve':
            self.compute_state = True
            if self.product_request_id:
                request_details = self.env['product.request'].sudo().search([('id', '=', self.product_request_id.id)], limit=1)
                if request_details:
                    pass
                    # request_details.status = 'requested'
                else:
                    pass
        else:
            self.compute_state = False


    @api.depends('approved_users')
    def compute_approved_user(self):
        if self.approved_users:
            for user in self.approved_users:
                print(user)
                if user.id in self.next_approve_user.ids:
                    self.next_approve_user -= user
                    self.user_approved = True
                else:
                    self.user_approved = False
        else:
            self.user_approved = False

    @api.depends('next_approve_user')
    def compute_is_an_approver(self):
        for rec in self:
            # rec.is_an_approver = self.env.user.id in rec.next_approve_user.mapped(
            #     'user_id.id') and self.env.user.id not in rec.approved_users.mapped('user_id.id')

        # for rec in self:
            rec.is_an_approver = self.env.user.id in rec.next_approve_user.mapped('id')

    @api.depends('total','qty','price')
    def compute_total_amount(self):
        total_amount = 0
        for total in self:
            if total.qty and total.price:
                total_amount += total.qty * total.price
        print("total_amount ", total_amount)
        self.total = total_amount

    def action_draft(self):
        print("draft")
        # self.state = 'draft'

    def action_request(self):
        print("reuested")
        # employee_data = self.env['hr.employee'].sudo().search([('user_id', '=', self.user_id.id)], limit=1)
        # if not employee_data.department_id:
        #     raise ValidationError("Employee data is empty")
        pr_company_data = self.env['pr.company'].sudo().search([('company_id', '=', self.company_id.id),

                                                                ('expense_type', '=', self.expense_type),
                                                                ('type', '=', 'lease')],
                                                               limit=1)
        if self.vendor_id.login:
            new_line_vals = {
                'user_id': self.vendor_id.login.id,
                'approve_order': int(1),
            }
            self.approve_line |= self.env['lease.approve.line'].create(new_line_vals)

        if pr_company_data:

            workflow_line_data = self.env['pr.approve.users'].sudo().search(
                [('pr_company_id', '=', pr_company_data.id)])  # searching in workflow line
            for approvers in workflow_line_data:
                line = []
                last_approve_order = None
                users_line = self.env['res.users.line'].sudo().search(
                    [('company_id', '=', approvers.company_id.id), ('branch_id', '=', approvers.branch_id.id),
                     ('department_id', '=', approvers.department_id.id),
                     ('designation', '=', approvers.designation.id)])  # searching user in users line
                print(users_line, "PR USERSSSSSSSSSSSSS")
                if users_line:
                    self.write({'approve_users': [(4, users_line.res_user_id.id)]})
                    vals = {
                        'user_id': users_line.res_user_id.id,
                        'company_id': approvers.company_id.id,
                        'branch_id': approvers.branch_id.id,
                        'department_id': approvers.department_id.id,
                        'designation': approvers.designation.id,
                        'approve_order': approvers.approve_order,

                    }
                    line.append((0, 0, vals))
                    if last_approve_order is None or approvers.approve_order > last_approve_order:
                        last_approve_order = approvers.approve_order
                    print(last_approve_order)
                self.approve_line = line

            # for approvers in pr_company_data.pr_approve_users_id:
            #     line = []
            #     last_approve_order = None
            #     for users in approvers:
            #         self.write({'approve_users': [(4, users.user_id.id)]})
            #         if self.vendor_id.user_id:
            #             approve_order = int(users.approve_order) + 1
            #         else:
            #             approve_order = users.approve_order
            #         vals = {
            #             'user_id': users.user_id.id,
            #             'company_id': users.company_id.id,
            #             # 'location': users.location.id,
            #             'department_id': pr_company_data.department_id.id,
            #             'designation': users.designation.id,
            #             'approve_order': approve_order,
            #         }
            #         line.append((0, 0, vals))
            #         if last_approve_order is None or users.approve_order > last_approve_order:
            #             last_approve_order = users.approve_order
            #         print(last_approve_order)
            #     self.approve_line = line

            next_approver_user_ids = [
                next_approver.user_id.id
                for next_approver in self.approve_line
                if (
                        (self.vendor_id.user_id and next_approver.approve_order == 1)
                        or (not self.vendor_id.user_id and next_approver.approve_order == 1)
                )
            ]

            print(next_approver_user_ids,"This print")
            if all(item is not False for item in next_approver_user_ids):
                self.write({'next_approve_user': [(6, 0, next_approver_user_ids)]})

                self.state ='request'

            model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
            pending_action = self.env['pending.actions'].sudo().search(
                [('model', '=', model.id), ('record', '=', self.id)], limit=1)
            if pending_action:
                user_ids_to_pass = self.approve_users.ids if self.approve_users else False
                pending_action.write({'approve_users': [(6, 0, user_ids_to_pass)]})
        else:
            print("WRK Flow not FOUND")




    def action_approve(self):
        print("Hellooo users")
        print(self.env.user.id)
        self.write({'approved_users': [(4, self.env.user.id)]})
        self.is_an_approver = False
        self.write({'next_approve_user': [(3, self.env.user.id)]})
        approver = self.env['lease.approve.line'].sudo().search(
            [('approve_lease_id', '=', self.id), ('user_id', '=', self.env.user.id)])
        for record in approver:
            record.write({'status': 'approve'})

        approve_users = self.env['lease.approve.line'].sudo().search(
            [('approve_lease_id', '=', self.id)], order='approve_order asc')

        user_ids = [{'u_id': user.user_id.id, 'order': user.approve_order} for user in approve_users]
        # user_ids = [{'u_id': user.user_id.id, 'order': user.approve_order} for user in approve_users]
        current_order = None
        next_user = None

        for user in user_ids:
            if self.env.user.id == user['u_id']:
                current_order = user['order']

        if current_order is not None:
            for user in user_ids:
                if user['order'] == current_order + 1:
                    next_user = user

        if next_user:
            next_user_id = next_user['u_id']
            next_order = next_user['order']
            self.write({'next_approve_user': [(4, next_user_id)]})

            print("Next User ID:", next_user_id)
            print("Next Order:", next_order)
        else:
            all_approved = all(approver.status == 'approve' for approver in approve_users)

            if all_approved:
                self.state = 'approve'

                model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
                pending_action = self.env['pending.actions'].sudo().search(
                    [('model', '=', model.id), ('record', '=', self.id)], limit=1)

                if pending_action:
                    pending_action.status = 'closed'

                if self.auto_po == True:
                    if self.with_gst and not self.tax:
                        raise UserError("Please add Tax")

                    print("approved")
                    products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)],
                                                                  limit=1)
                    # print(products)
                    for product in products:
                        # print(product)
                        order_line = [(0, 0, {
                            'display_type': False,
                            'name': products.name or '',
                            'product_id': products.id,
                            'price_unit': self.price,
                            'product_qty': self.qty,
                            'taxes_id': [(6, 0, [self.tax.id])] if self.tax else [],
                            'product_uom': self.product_id.uom_po_id.id,
                        })]
                        # print(order_line)
                        purchase_order = self.env['purchase.order'].create({
                            'partner_id': self.vendor_id.id,
                            'order_line': order_line,
                            'company_id': self.company_id.id,
                            'location': self.company_id.id,
                            'user_id': self.user_id.id,
                            'expense_type': self.product_request_id.expense_type or '',
                            'exp_category': self.exp_category.id,
                            'department_id': self.product_request_id.department_id.id or '',
                            'bill_to': self.product_request_id.bill_to.id or self.company_id.id,
                            'ship_to': self.product_request_id.ship_to.id or self.company_id.id,
                            'is_auto_po': True,
                            'is_readonly':True
                        })
                        self.env.cr.commit()


                        if self.auto_invoice == True:
                            purchase_order.button_confirm()
                            for lines in purchase_order.order_line:
                                lines.qty_received = lines.product_qty
                            purchase_order.action_create_invoice()



                        po_vals = {
                            'po': purchase_order.id,
                            'date': fields.Date.today(),
                            'status': purchase_order.state,
                            'recurring_lease_id': self.id
                        }

                        po_create = self.env['lease.recurring.po'].create(
                            po_vals
                        )
                        self.env.cr.commit()

                # Change the state to the desired value when all statuses are 'approve'
                # self.write({'state': 'approved_state'})
            else:
                # Handle the case when not all statuses are 'approve'
                # self.write({'state': 'pending_state'})
                print("not approved")

            # self.state = 'approve'
            print("Current user is the last approver or not found.")

        # for users in approve_users:
        #     print(users.approve_order)
        #     if self.env.user.id == users.user_id.id:

                # self.next_approve_user.write()


        # print(user_ids)
        # for user in user_ids:
        #     if self.env.user.id == user['u_id']:
        #         self.next_approve_user = user_ids[user_ids.index(user) + 1]['u_id']

        # for app in approve_users:
        #     print(app.user_id.name)
        #     print(app.approve_order)

        # print(self.approve_users.mapped('user_id.id'))
        # if (self.env.user.id in self.approve_users.mapped('user_id.id') and
        #         self.env.user.id in self.next_approve_user.mapped('user_id.id')):
        #     self.write({'approved_users': [(4, self.env.user.id)]})
        #
        # else:
        #     raise ValidationError("Please make sure the user in approval list.")

    def action_reject(self):
        print("helloo rejected")
        self.state = 'reject'
        for approvers in self.approve_line:
            if approvers.user_id.id == self.env.user.id:
                approvers.write({'status': 'cancel'})

    @api.onchange('bill_to')
    def _onchange_bill_to(self):
        if self.bill_to:
            self.ship_to = self.bill_to

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('product.lease') or _('New')
        res = super(ProductLease, self).create(vals)

        model = self.env['ir.model'].sudo().search([('model', '=', self._name)],limit=1)
        pending_vals = {
            'model': model.id,
            'name': res.name,
            'record': res.id,
            'date': date.today(),
        }
        pendings = self.env['pending.actions'].create(pending_vals)

        return res

    class ProductLeaseLine(models.Model):
        _name = "lease.product.line"
        _description = "Product Lease"

        product_id = fields.Many2one('product.template', string="Product", store=True, force_save=True, required=True)
        vendors = fields.Many2many('res.partner', "lease_vendors", "lease_line", "vendor", string="Vendors",
                                   required=True)
        payment_terms = fields.Many2one('account.payment.term', "Payment Terms", required=True)
        qty = fields.Float(string="Quantity", required=True)
        unit_price = fields.Float(string="Unit Price", required=True)
        sub_total = fields.Float("SubTotal", readonly=True, compute="compute_sub_total")
        expected_date = fields.Date(string="Needed Date", required=True)
        contract_status = fields.Selection(
            selection=[('new', 'New'), ('in_contract', 'In Contract')],
            string='Contract',
            default='new',
            required=True
        )

        lease_id = fields.Many2one('product.lease', string='Lease Id',
                                   invisible=True)

        @api.depends('qty', 'unit_price')
        def compute_sub_total(self):
            for rec in self:
                if rec.qty and rec.unit_price:
                    rec.sub_total = rec.qty * rec.unit_price
                else:
                    rec.sub_total = ''

    class LeaseApproveLine(models.Model):
        _name = "lease.approve.line"
        _description = "Approve Lines"

        approve_lease_id = fields.Many2one('product.lease', string='Lease Approve',
                                           invisible=True)

        user_id = fields.Many2one('res.users', string="User")
        company_id = fields.Many2one('res.company', string="Company")
        # location = fields.Many2one('res.company', string="Location")
        branch_id = fields.Many2one('res.branch', string="Branch")
        department_id = fields.Many2one('hr.department', string="Department")
        emp_name = fields.Many2one('hr.employee', string="Employee")
        designation = fields.Many2one('hr.job', string="Designation")
        approve_order = fields.Integer(string="Order")
        status = fields.Selection(
            selection=[('draft', 'Draft'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('deligate', 'Deligated')],
            string='Status',
            default='draft',
            required=True, tracking=True
        )


    class LeaseReccuringPO(models.Model):
        _name = "lease.recurring.po"
        _description = "Reccuring PO"

        recurring_lease_id = fields.Many2one('product.lease', string='Lease Reccuring PO',
                                           invisible=True)

        po = fields.Many2one("purchase.order",string="PO")
        status = fields.Char(string="State")
        date = fields.Date("Date")




