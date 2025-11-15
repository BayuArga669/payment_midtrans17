from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    midtrans_server_key = fields.Char(string="Midtrans Server Key", config_parameter="payment_midtrans.server_key")
    midtrans_client_key = fields.Char(string="Midtrans Client Key", config_parameter="payment_midtrans.client_key")
    midtrans_merchant_id = fields.Char(string="Midtrans Merchant ID", config_parameter="payment_midtrans.merchant_id")
