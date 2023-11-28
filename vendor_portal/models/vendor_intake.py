from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo import modules
from odoo.http import request, _logger
import requests


class VendorIntake(models.Model):
    _name = 'vendor.intake'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # name = fields.Char(string='Number', required=True, copy=False, readonly=True,
    #                        default=lambda self: _('New'))
    name = fields.Char("Name", tracking=True)
    street = fields.Char("Street")
    address1 = fields.Char("Address 1")
    address2 = fields.Char("Address 2")
    city = fields.Char("City")
    zip = fields.Char("Pincode")
    gst = fields.Char("VAT No", tracking=True)
    pan = fields.Char("Pan No", tracking=True)
    tel = fields.Char("Telephone No", tracking=True)
    mob = fields.Char("Mobile No", tracking=True)
    mail_id = fields.Char("Email ID", tracking=True)
    state_id = fields.Char("State")
    state_ids = fields.Many2one('res.country.state', "State")
    country_id = fields.Many2one(string="Country", comodel_name='res.country', help="Country")
    # user_id = fields.Many2one('res.users', string='Contact User', default=lambda self: self.env.user,)
    ref = fields.Char("Vendor Reference")
    contactperson = fields.Char("Contact Person 1")
    contactperson2 = fields.Char("Contact Person 2")
    msme = fields.Char("MSME Category")
    remarks = fields.Text("Remarks")
    states = fields.Selection(
        [("draft", "Draft"), ("review","Review"),("approved", "Approved"), ("done", "User Generated"), ("cancelled", "Cancel")],
        string="Status", default="draft", tracking=True)

    bank = fields.Char(string='Bank Name')
    bank_acc_no = fields.Char(string='Account No')
    branch = fields.Char(string="Branch")
    ifsc = fields.Char(string="IFSC Code")

    msme_number = fields.Char(string="MSME Number")
    vendor_category = fields.Many2one("product.category", string="Vendor Category")
    # company_type = fields.Char(string="Company Type")
    company_type = fields.Selection([
        ('type1', 'Companies Limited by Shares'),
        ('type2', 'Companies Limited by Guarantee'),
        ('type3', 'Unlimited Companies'),
        ('type4', 'One Person Companies (OPC)'),
        ('type5', 'Private Companies'),
        ('type6', 'Public Companies'),
        ('type7', 'Holding and Subsidiary Companies'),
        ('type8', 'Associate Companies'),
        ('type9', 'Companies in terms of Access to Capital'),
        ('type10', 'Government Companies'),
        ('type11', 'Foreign Companies'),
        ('type12', 'Charitable Companies'),
        ('type13', 'Dormant Companies'),
        ('type14', 'Nidhi Companies'),
        ('type15', 'Public Financial Institutions'),
    ], string="Company Type")
    website = fields.Char(string="Website Link")
    gst_file = fields.Binary(string='Uploaded File')
    pan_card = fields.Binary(string='Pan Card file')
    bank_file = fields.Binary(string='Statement Copy file')
    bank_cheque_file = fields.Binary(string='Bank Cheque file')
    vendor_approve_users = fields.Many2many(
        'res.users',
        'vendor_request_approve_users_rel',
        'request_id',
        'user_id',
        string='Approve Users',
    )

    vendor_approved_users = fields.Many2many(
        'res.users',
        'vendor_request_approved_users_rel',
        'request_id',
        'user_id',
        string='Approved Users',
    )

    approve_check = fields.Boolean(compute="_approve_check", string="Approve Check", default=False)
    next_approve_user_id = fields.Many2many('res.users', string="Next Approve User ID")
    user_approve_check = fields.Boolean(string="User Approve check", compute="_compute_total", default=False)
    vendor_approve_line = fields.One2many('vendor.approve.line',
                                          'vendor_intake_id',
                                          string='Vendor Approve Line',
                                          tracking=True)
    company_id = fields.Many2one("res.company","Company")
    location = fields.Many2one("res.company","Location")
    department = fields.Many2one("hr.department", "Department", domain="[('company_id', '=', company_id)]")
    vendor_representative = fields.Many2one("res.users","Representative")
    approve_users = fields.Many2many(
        'res.users',
        'rel_vd_apprvers',
        'vd_id',
        'users_v',
        string='Approve Users',
    )
    approved_users = fields.Many2many(
        'res.users',
        'approved_vd_relation',
        'vd_apprved',
        'user_id_vd',
        string='Approved Users',
    )

    next_approve_user = fields.Many2many(
        'res.users',
        'next_aprved_vd',
        'next_vd',
        'users_id_vd',
        string='Next Approver', )
    is_an_approver = fields.Boolean("Approver",compute='compute_is_an_approver')

    @api.depends('next_approve_user')
    def compute_is_an_approver(self):
        for rec in self:
            rec.is_an_approver = self.env.user.id in rec.next_approve_user.mapped('id')


    def action_review(self):
        if not self.company_id or not self.department or not self.location:
            raise UserError("Please fill in all Company Details: Company, Department, and Location")
        vendor_approval = request.env['vendor.approval'].sudo().search([('company_id', '=', self.company_id.id),
                                     ('department_id', '=', self.department.id),('location', '=', self.location.id)], limit=1)
        if vendor_approval:
            line = []
            for approvers in vendor_approval.vendor_approve_users_id:
                self.write({'approve_users': [(4, approvers.user_id.id)]})
                vals = {
                    'user_id': approvers.user_id.id,
                    'company_id': approvers.company_id.id,
                    'location': approvers.location.id,
                    'department_id': approvers.department_id.id,
                    'designation': approvers.designation.id,
                    'approve_order': approvers.approve_order,
                }
                line.append((0, 0, vals))
            self.vendor_approve_line = line
            next_approver_user_ids = [next_approver.user_id.id for next_approver in self.vendor_approve_line if
                                      next_approver.approve_order == 1]
            print(next_approver_user_ids, "This print")
            if all(item is not False for item in next_approver_user_ids):
                self.write({'next_approve_user': [(6, 0, next_approver_user_ids)]})
                self.states = 'review'
        else:
            raise UserError("No vendor workflow found for this company")

    @api.depends("user_approve_check")
    def _compute_total(self):
        print('Inside user_approve_check')
        for rec in self:
            if self.env.user in rec.next_approve_user_id:
                rec.user_approve_check = True
            else:
                rec.user_approve_check = False

    def _approve_check(self):
        self.approve_check = False
        if self.vendor_approved_users and (self.env.user.id in [user_ids.id for user_ids in self.vendor_approved_users]):
            self.approve_check = True
            print("True")
        else:
            self.approve_check = False
            print(self.states)
            print("False")

    def action_approve(self):
        self.ref = self.env['ir.sequence'].next_by_code('vendor.intake')
        self.states = 'approved'

    def action_done(self):
        if self.gst and self.mail_id:
            vendor_exist = self.env['res.partner'].sudo().search([
                ('vat', '=', self.gst)])
            if vendor_exist:
                raise UserError("Vendor GST is already exist")
            else:
                vendor_generated = self.env['res.partner'].sudo().create({
                    "name": self.name,
                    "street": self.address1,
                    "street2": self.street,
                    "city": self.city,
                    # "state_id":self.state_id.id,
                    "zip": self.zip,
                    # "country_id":self.country_id.id,
                    "email": self.mail_id,
                    "vat": self.gst,
                    # "mobile": self.mob,
                })

            if vendor_generated:

                user_exist = self.env['res.users'].sudo().search([('name', '=', self.name),
                                                                  ('login', '=', self.mail_id)])
                if user_exist:
                    raise UserError("Login already exist")
                else:
                    password = self.ref
                    user_generated = self.env['res.users'].sudo().create({
                        'name': self.name,
                        'login': self.mail_id,
                        'password': password,
                        'partner_id': vendor_generated.id,
                        # 'sel_groups_1_9_10': "1",  # Assign group 1
                        # 'sel_groups_58_59': "58",  # Assign group 58
                        # 'in_group_76': True,
                    })
            body = (
                    "Dear Vendor,Your vendor registration has been successfully approved and your Login id is" + " " + self.mail_id + " "
                                                                                                                                      "Password is" + " " + password)
            vals = {
                'subject': 'Vendor Login Credentials',
                'body_html': body,
                'email_to': self.mail_id,
                'auto_delete': False,
                # 'email_from': ,
            }
            # print(vals)
            mail_id = self.env['mail.mail'].sudo().create(vals)
            mail_id.sudo().send()
            self.states = 'done'
        else:
            raise UserError("Please ensure GST and Mail Id are entered correctly")

    def action_draft(self):
        if self.states == "done":
            user_found = self.env['res.users'].sudo().search([('name', '=', self.name),
                                                              ('login', '=', self.mail_id)])
            if user_found:
                raise UserError("Please delete the related User & Vendor to countinue")
            else:
                self.states = 'approved'

        else:
            self.states = 'draft'
            self.approve_users = [(5, 0, 0)]
            self.next_approve_user = [(5, 0, 0)]
            self.approved_users = [(5, 0, 0)]
            self.vendor_approve_line.unlink()

    def action_approval(self):
        print("Hellooo users")
        print(self.env.user.id)
        self.write({'approved_users': [(4, self.env.user.id)]})
        # self.is_an_approver = False
        self.write({'next_approve_user': [(3, self.env.user.id)]})
        approver = self.env['vendor.approve.line'].sudo().search(
            [('vendor_intake_id', '=', self.id), ('user_id', '=', self.env.user.id)])
        for record in approver:
            record.write({'status': 'accept'})

        approve_users = self.env['vendor.approve.line'].sudo().search(
            [('vendor_intake_id', '=', self.id)], order='approve_order asc')

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
            all_approved = all(approver.status == 'accept' for approver in approve_users)

            if all_approved:
                self.states = 'approved'
                self.ref = self.env['ir.sequence'].next_by_code('vendor.intake')


                # Change the state to the desired value when all statuses are 'approve'
                # self.write({'state': 'approved_state'})
            else:
                # Handle the case when not all statuses are 'approve'
                # self.write({'state': 'pending_state'})
                print("not approved")

            # self.state = 'approve'
            print("Current user is the last approver or not found.")







        # self.write({'vendor_approved_users': [(4, self.env.user.id)]})
        # # print(self.approve_users)
        # # print(self.approved_users)
        # approve_users = self.env['vendor.approve.line'].sudo().search(
        #     [('vendor_intake_id', '=', self.id), ('user_id', '=', self.env.user.id)], limit=1)
        #
        # approve_users.write({
        #     'status': 'accept'
        # })
        #
        # if self.vendor_approved_users == self.vendor_approve_users:
        #     self.states = 'approved'
        #     self.action_done()
        # else:
        #     approve_users = self.env['vendor.approve.line'].sudo().search([('vendor_intake_id', '=', self.id)],
        #                                                                   order='approve_order asc')
        #
        #     user_ids = [{'u_id': user.user_id.id, 'order': user.approve_order} for user in approve_users]
        #     # print(user_ids)
        #
        #     order_list = list(set([order_id.approve_order for order_id in approve_users]))
        #     order_list.sort()
        #     approve_dict = {}
        #     print("order_list ", order_list)
        #     for order in order_list:
        #         for user in user_ids:
        #             if user['order'] == order:
        #                 if order in approve_dict:
        #                     approve_dict[order].append({'u_id': user['u_id'], 'order': user['order']})
        #                 else:
        #                     approve_dict[order] = [{'u_id': user['u_id'], 'order': user['order']}]
        #
        #     print("approve_dict ", approve_dict)
        #
        #     record_to_remove = self.env['res.users'].browse(self.env.user.id)
        #     self.next_approve_user_id -= record_to_remove
        #
        #     if not self.next_approve_user_id:
        #         for order in order_list:
        #             for order_list_users in approve_dict[order]:
        #                 if self.env.user.id == order_list_users['u_id']:
        #                     try:
        #                         if approve_dict[order + 1]:
        #                             for users in approve_dict[order + 1]:
        #                                 self.write({'next_approve_user_id': [(4, users['u_id'])]})
        #                     except:
        #                         print("order+1 ", order + 1)
        #                         print("order_list[-1] ", order_list[-1])
        #                         flag = 0
        #                         for i in range(order + 1, order_list[-1] + 1):
        #                             print("i: ", i)
        #                             print("len(order_list) : ", len(order_list))
        #                             try:
        #                                 if approve_dict[i]:
        #                                     for users in approve_dict[i]:
        #                                         print("write")
        #                                         self.write({'next_approve_user_id': [(4, users['u_id'])]})
        #                                         flag = 1
        #                             except:
        #                                 print("pass")
        #                                 pass
        #                             if flag:
        #                                 break

    def action_decline(self):
        self.states = 'cancelled'


class VendorApproveLine(models.Model):
    _name = "vendor.approve.line"
    _description = "Vendor Approve Line"

    vendor_intake_id = fields.Many2one('vendor.intake', string='Product Request Id',
                                       invisible=True)

    user_id = fields.Many2one('res.users', string="User")
    company_id = fields.Many2one('res.company', string="Company Id")
    location = fields.Many2one('res.company', string="Location")
    department_id = fields.Many2one('hr.department', string="Department")
    emp_name = fields.Many2one('hr.employee', string="Employee")
    designation = fields.Many2one('hr.job', string="Designation")
    approve_order = fields.Integer(string="Order")
    status = fields.Selection(
        selection=[('draft', 'Draft'), ('accept', 'Accept'), ('cancel', 'Cancel'), ('delegate', 'Delegated')],
        string='Status',
        default='draft',
        required=True, tracking=True
    )
