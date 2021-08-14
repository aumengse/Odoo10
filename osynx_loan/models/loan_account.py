from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class LoanAccount(models.Model):
    _name = 'loan.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Account'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner',string="Guarantor")
    borrower_id = fields.Many2one('res.partner',string="Borrower")
    date_from = fields.Date(string="Start")
    date_to = fields.Date(string="End", compute='compute_date_to')
    principal = fields.Float(string="Principal Amount")
    term = fields.Integer(string="Term")
    interest = fields.Many2one('loan.interest',string="Interest")
    state = fields.Selection([('draft', "Draft"),
                              ('queue', "On Queue"),
                              ('approve', "Approved")
                              ], default='draft', string="State")
    line_ids = fields.One2many('loan.account.line','loan_id',string="Loan Schedule")

    @api.depends('date_from', 'term')
    def compute_date_to(self):
        for rec in self:
            rec.date_to = False
            if rec.date_from:
                rec.date_to = rec.date_from + relativedelta(months=1)

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('loan.account.sequence')
        vals.update({
            'name': name
        })
        res = super(LoanAccount, self).create(vals)
        return res

    class LoanAccountLine(models.Model):
        _name = 'loan.account.line'
        _description = 'Loan Account Line'

        name = fields.Char(string="Name")
        date = fields.Date(string="Due Date")
        amount = fields.Float(string="Amount")
        state = fields.Selection([('unpaid', "Unpaid"),
                                  ('paid', "Paid"),
                                  ], default='unpaid', string="State")
        loan_id = fields.Many2one('loan.account', string="Loan")
