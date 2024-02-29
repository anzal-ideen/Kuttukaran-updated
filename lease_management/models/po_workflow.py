from datetime import datetime
from datetime import date

from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError, UserError
from odoo.exceptions import Warning


class PurchaseApprovals(models.Model):
    _inherit = "purchase.order"



    approvers_line_ids = fields.One2many('po.approve.line',
                                         'po_approve_id',
                                         string='Purchase Approve Line',
                                         tracking=True)
    is_confirmed = fields.Boolean("Is Confirmed")
    is_auto_po = fields.Boolean("Automated PO")
    is_an_approver = fields.Boolean("Approver",compute='compute_is_an_approver')


    approve_users = fields.Many2many(
        'res.users',
        'rel_po_apprvers',
        'po_id',
        'po_user',
        string='Approve Users',
    )
    approved_users = fields.Many2many(
        'res.users',
        'approved_po_relation',
        'po_apprved',
        'po_user_id',
        string='Approved Users',
    )

    next_approve_user = fields.Many2many(
        'res.users',
        'next_aprved_po',
        'next_po',
        'po_users_id',
        string='Next Approver', )

    in_budget = fields.Boolean("In Budget",compute="_compute_inbudget",readonly=False,default=True,store=True,force_save=True)






    @api.depends('pr_budget_id', 'amount_total')
    def _compute_inbudget(self):
        for rec in self:
            if rec.pr_budget_id and rec.amount_total:
                if rec.pr_budget_id.amount_available < 0:
                    rec.in_budget = False
            else:
                rec.in_budget = True

    @api.depends('next_approve_user')
    def compute_is_an_approver(self):
        for rec in self:
            rec.is_an_approver = self.env.user.id in rec.next_approve_user.mapped('id')

    def button_confirm(self):
        print("helllooo worldddd")
        if self.is_auto_po == False:
            if self.is_confirmed != True:

                if self.pr_budget_id:
                    self.pr_budget_id.amount_used += self.amount_total
                    self._compute_inbudget()

                pr_company_data = self.env['pr.company'].sudo().search([
                    ('company_id', '=', self.company_id.id),
                    # ('company_id', '=', self.env.company.id),
                    # ('branch_id','=',self.branch_id.id),
                    # ('department_id', '=',self.department_id.id),
                    ('expense_type', '=',self.expense_type),
                    # ('exp_category', '=',self.exp_category.id),
                    ('from_amount', '<=', self.amount_total),
                    ('to_amount', '>=', self.amount_total),
                    ('type','=','purchase')],
                   limit=1)
                print(pr_company_data.name)
                if pr_company_data:
                    # self.message_post(body="Wait for PO"+" "+ self.name+" " +"Approval")

                    if self.partner_id.login:
                        new_line_vals = {
                            'user_id': self.partner_id.login.id,
                            'approve_order': int(1),
                        }
                        self.approvers_line_ids |= self.env['po.approve.line'].create(new_line_vals)
                        self.message_post(body="Wait for Vendor acknowledgement")

                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        menu_id = self.env['ir.ui.menu'].sudo().search(
                            [('name', '=', 'Purchase')], limit=1) or False

                        url_params = {
                            'id': self.id,
                            'action': self.env.ref('vendor_po.action_view_vendors_po').id,
                            'model': 'purchase.order',
                            'view_type': 'form',
                            'menu_id': menu_id.id if menu_id else False,
                            'function': 'action_approval',
                        }

                        params = '/web?#%s' % url_encode(url_params)
                        approval_url = base_url + params if base_url else "#"

                        print("appppppppppppppppppppppppppppprovalllllllllllllll", approval_url)

                        # body = f"Dear User,A Purchase Order {self.name} has been initiated."
                        author = self.env['res.partner'].sudo().search(
                            [('name', '=', 'Administrator')], limit=1) or False

                        body = (
                            f"Dear Vendor,A Purchase Order {self.name} has been raised and waiting for your acknowledgement.<br><br>"
                            f"<a href='{approval_url}' style='display: inline-block; padding: 10px 20px; "
                            f"background-color: #008CBA; color: white; text-align: center; text-decoration: none; "
                            f"font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px;'>View Entries</a> <br>"

                            # f"<a href='{approval_url}' style='display: inline-block; padding: 10px 20px; "
                            # f"background-color: #4CAF50; color: white; text-align: center; text-decoration: none; "
                            # f"font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px;'>Approve</a> <space>"
                            # f"<a href='http://your_domain/reject' style='display: inline-block; padding: 10px 20px; "
                            # f"background-color: #F44336; color: white; text-align: center; text-decoration: none; "
                            # f"font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px;'>Reject</a><br>"

                        )

                        if self.partner_id.email:
                            mail_values = {
                                'subject': 'PO Waiting for acknowledgment',
                                'body_html': body,
                                'email_to': self.partner_id.email,
                                'auto_delete': False,
                                'author_id': author.id
                            }
                            mail_record = self.env['mail.mail'].sudo().create(mail_values)


                    self.message_post(body="Wait for PO Approval")
                    for approvers in pr_company_data.pr_approve_users_id:
                        line = []
                        last_approve_order = None
                        print(approvers)
                        # for users in approvers:

                            # print(users_line)

                        for users in approvers:
                            users_line = self.env['res.users.line'].sudo().search(
                                [('company_id', '=', users.company_id.id),
                                 ('branch_id', '=', users.branch_id.id),
                                 ('department_id', '=', users.department_id.id),
                                 ('designation', '=', users.designation.id)])

                            self.write({'approve_users': [(4, users_line.res_user_id.id)]})
                            if self.partner_id.login:
                                approve_order = int(users.approve_order) + 1
                            else:
                                approve_order = users.approve_order
                            vals = {
                                'user_id': users_line.res_user_id.id,
                                'company_id': users.company_id.id,
                                'branch_id': users.branch_id.id,
                                'department_id': users.department_id.id,
                                'designation': users.designation.id,
                                'approve_order': approve_order,
                            }
                            line.append((0, 0, vals))
                            if last_approve_order is None or users.approve_order > last_approve_order:
                                last_approve_order = users.approve_order
                            print(last_approve_order)
                            print(line)
                        self.approvers_line_ids = line
                    next_approver_user_ids = [next_approver.user_id.id for next_approver in self.approvers_line_ids if
                                              next_approver.approve_order == 1]
                    print(next_approver_user_ids, "This print")
                    if all(item is not False for item in next_approver_user_ids):
                        self.write({'next_approve_user': [(6, 0, next_approver_user_ids)]})
                        self.is_confirmed = True
                    #
                        model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
                        pending_vals = {
                            'model': model.id,
                            'name': self.name,
                            'record': self.id,
                            'date': date.today(),
                            'approve_users': [(6, 0, self.approvers_line_ids.mapped('user_id').ids)]
                        }
                        pendings = self.env['pending.actions'].create(pending_vals)

                        activity_type = self.env['mail.activity.type'].sudo().search([('name', '=', 'Pending Purchase Order')],
                                                                                     limit=1)
                        activity_type_id = activity_type.id if activity_type else False
                        res_model_id = self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id
                        for approver_line in self.next_approve_user:
                            activity_values = {
                                'user_id': approver_line.id,
                                'res_id': self.id,
                                'note': "Pending Action",
                                'activity_type_id': activity_type_id,
                                'res_model_id': res_model_id,
                            }
                            created_activity = self.env['mail.activity'].create(activity_values)

                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        menu_id = self.env['ir.ui.menu'].sudo().search(
                            [('name', '=', 'Purchase')], limit=1) or False

                        url_params = {
                            'id': self.id,
                            'action': self.env.ref('vendor_po.action_view_vendors_po').id,
                            'model': 'purchase.order',
                            'view_type': 'form',
                            'menu_id': menu_id.id if menu_id else False,
                            # 'function': 'action_approval',
                        }

                        params = '/web?#%s' % url_encode(url_params)
                        approval_url = base_url + params if base_url else "#"

                        print("appppppppppppppppppppppppppppprovalllllllllllllll", approval_url)
                        author = self.env['res.partner'].sudo().search(
                            [('name', '=', 'Administrator')], limit=1) or False

                        body = (
                            f"Dear User,A Purchase Order {self.name} has been raised and waiting for your approval.<br><br>"
                            f"<a href='{approval_url}' style='display: inline-block; padding: 10px 20px; "
                            f"background-color: #008CBA; color: white; text-align: center; text-decoration: none; "
                            f"font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px;'>View Entries</a> <br>"

                        )
                        if author:
                            mail_values = {
                                'subject': 'PO Waiting for Approval',
                                'body_html': body,
                                'email_to': self.next_approve_user.login,
                                'auto_delete': False,
                                'author_id': author.id
                            }
                            mail_record = self.env['mail.mail'].sudo().create(mail_values)


                    else:
                        res = super(PurchaseApprovals, self).button_confirm()
                else:
                    # raise UserError("Please make sure all the approvers approved or not")
                    res = super(PurchaseApprovals, self).button_confirm()
                    return res
            else:
                res = super(PurchaseApprovals, self).button_confirm()
                return res
        else:
            if self.pr_budget_id:
                self.pr_budget_id.amount_used += self.amount_total
            res = super(PurchaseApprovals, self).button_confirm()
            return res

    def action_approval(self):
        self.message_post(body=self.env.user.name +" "+"Approved")
        print("approvee")
        print("Hellooo users")
        print(self.env.user.id)
        self.write({'approved_users': [(4, self.env.user.id)]})
        self.is_an_approver = False
        self.write({'next_approve_user': [(3, self.env.user.id)]})
        approver = self.env['po.approve.line'].sudo().search(
            [('po_approve_id', '=', self.id), ('user_id', '=', self.env.user.id)])
        for record in approver:
            record.write({'status': 'approve'})

            model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
            pending_action = self.env['pending.actions'].sudo().search(
                [('model', '=', model.id), ('record', '=', self.id)], limit=1)

            if pending_action:
                pending_action.status = 'closed'

            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Pending Purchase Order')], limit=1)
            print("type is", self.env.user.id)
            activity = self.env['mail.activity'].search([
                ('res_model_id', '=', self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id),
                ('user_id', '=', self.env.user.id), ('res_name', '=', self.name),
                ('activity_type_id', '=', activity_type.id),
            ], limit=1)
            if activity:
                print(activity.id)
                activity.action_feedback(feedback="Activity completed")

        approve_users = self.env['po.approve.line'].sudo().search(
            [('po_approve_id', '=', self.id)], order='approve_order asc')

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

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            menu_id = self.env['ir.ui.menu'].sudo().search(
                [('name', '=', 'Purchase')], limit=1) or False

            url_params = {
                'id': self.id,
                'action': self.env.ref('purchase.purchase_rfq').id,
                'model': 'purchase.order',
                'view_type': 'form',
                # 'menu_id': self.env.ref('product_purchase.product_purchase').id,
                'menu_id': menu_id.id,
            }
            params = '/web?#%s' % url_encode(url_params)
            view_url = base_url + params if base_url else "#"

            author = self.env['res.partner'].sudo().search(
                [('name', '=', 'Administrator')], limit=1) or False

            body = (
                f"Dear User,A Purchase Order {self.name} is waiting for Approval.<br><br>"
                f"<a href='{view_url}' style='display: inline-block; padding: 10px 20px; "
                f"background-color: #008CBA; color: white; text-align: center; text-decoration: none; "
                f"font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px;'>View Entries</a> <br>"

            )
            for user in self.next_approve_user:
                model = self.env['ir.model'].sudo().search([('model', '=', self._name)],
                                                           limit=1)
                pending_vals = {
                    'model': model.id,
                    'name': self.name + " " + "Waiting For Approval",
                    'record': self.id,
                    'date': date.today(),
                }
                if user:
                    user_ids_to_pass = user.ids
                    pending_vals['approve_users'] = [(6, 0, user_ids_to_pass)]
                    pendings = self.env['pending.actions'].create(pending_vals)

                    activity_type = self.env['mail.activity.type'].sudo().search([('name', '=', 'Pending Purchase Order')],
                                                                                 limit=1)
                    activity_type_id = activity_type.id if activity_type else False
                    res_model_id = self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id
                    # for approver_line in self.next_approve_user:
                    activity_values = {
                        'user_id': user.id,
                        'res_id': self.id,
                        'note': "Pending Action",
                        'activity_type_id': activity_type_id,
                        'res_model_id': res_model_id,
                    }
                    created_activity = self.env['mail.activity'].create(activity_values)

                if user.login:
                    subject = "Purchase Order Waiting For APPROVAL: %s" % self.name
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_to': user.login,
                        'auto_delete': False,
                        'author_id': author.id
                    }
                    mail_record = self.env['mail.mail'].sudo().create(mail_values)

            print("Next User ID:", next_user_id)
            print("Next Order:", next_order)
        else:
            all_approved = all(approver.status == 'approve' for approver in approve_users)

            if all_approved:
                self.is_confirmed = True
                model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
                pending_action = self.env['pending.actions'].sudo().search(
                    [('model', '=', model.id), ('record', '=', self.id)], limit=1)

                if pending_action:
                    pending_action.status = 'closed'

                activity_type = self.env['mail.activity.type'].search([('name', '=', 'Pending Purchase Order')],
                                                                      limit=1)
                print("type is", self.env.user.id)
                activity = self.env['mail.activity'].search([
                    ('res_model_id', '=', self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id),
                    ('user_id', '=', self.env.user.id), ('res_name', '=', self.name),
                    ('activity_type_id', '=', activity_type.id),
                ], limit=1)
                if activity:
                    print(activity.id)
                    activity.action_feedback(feedback="Activity completed")

                author = self.env['res.partner'].sudo().search(
                    [('name', '=', 'Administrator')], limit=1) or False
                mail_values = {
                    'subject': "PO Confirmed",
                    'body_html': "Dear Vendor,The Purchase Order has been confirmed ",
                    'email_to': self.partner_id.email,
                    'auto_delete': False,
                    'author_id': author.id
                }
                mail_record = self.env['mail.mail'].sudo().create(mail_values)

                self.button_confirm()
                self.button_confirm()
                # self.state = 'approve'
                print("approved")
                print("Confirmedddddddddddddddddddddddddddddddddddddddddddddddddddd")
                # self.write({'state': 'approved_state'})
            else:
                # Handle the case when not all statuses are 'approve'
                # self.write({'state': 'pending_state'})
                print("not approved")

            # self.state = 'approve'
            print("Current user is the last approver or not found.")
            self.button_confirm()

    def action_rejected(self):
        print("rejectttt")
        model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
        pending_action = self.env['pending.actions'].sudo().search(
            [('model', '=', model.id), ('record', '=', self.id)])

        if pending_action:
            for i in pending_action:
                i.status = 'closed'

        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Pending Purchase Order')],
                                                              limit=1)
        print("type is", self.env.user.id)
        activity = self.env['mail.activity'].search([
            ('res_model_id', '=', self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id),
             ('res_name', '=', self.name),
            ('activity_type_id', '=', activity_type.id),
        ])
        if activity:
            for i in activity:
                i.action_feedback(feedback="Activity Cancelled")

        self.message_post(body=self.env.user.name + " " + "Rejected")
        self.write({
            'state': 'cancel',
            'is_confirmed': False,
            'approvers_line_ids': [(5, 0, 0)],
            'approve_users': [(5, 0, 0)],
            'approved_users': [(5, 0, 0)],
            'next_approve_user': [(5, 0, 0)],
        })

    def button_cancel(self):
        res = super(PurchaseApprovals, self).button_cancel()
        model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
        pending_action = self.env['pending.actions'].sudo().search(
            [('model', '=', model.id), ('record', '=', self.id)], limit=1)

        if pending_action:
            for i in pending_action:
                i.status = 'closed'
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Pending Purchase Order')],
                                                              limit=1)
        print("type is", self.env.user.id)
        activity = self.env['mail.activity'].search([
            ('res_model_id', '=', self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id),
            ('res_name', '=', self.name),
            ('activity_type_id', '=', activity_type.id),
        ])
        if activity:
            for i in activity:
                i.action_feedback(feedback="Activity Cancelled")

        self.write({
            'state': 'cancel',
            'is_confirmed': False,
            'approvers_line_ids': [(5, 0, 0)],
            'approve_users': [(5, 0, 0)],
            'approved_users': [(5, 0, 0)],
            'next_approve_user': [(5, 0, 0)],
        })

        return res


class PoApproveLines(models.Model):
    _name = "po.approve.line"
    _description = "PO Approvers Lines"

    po_approve_id = fields.Many2one('purchase.order', string='PO Approve',
                                    invisible=True)

    user_id = fields.Many2one('res.users', string="User")
    company_id = fields.Many2one('res.company', string="Company")
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
