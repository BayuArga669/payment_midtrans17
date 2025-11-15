from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('midtrans', 'Midtrans')])
    midtrans_snap_url = fields.Char(default="https://app.sandbox.midtrans.com/snap/v1/transactions")
