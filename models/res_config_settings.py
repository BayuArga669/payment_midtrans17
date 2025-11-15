from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    midtrans_client_key = fields.Char("Midtrans Client Key")
    midtrans_server_key = fields.Char("Midtrans Server Key")
    midtrans_mode = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production')
    ], default='sandbox')
    