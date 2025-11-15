from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    midtrans_client_key = fields.Char("Midtrans Client Key")
    midtrans_server_key = fields.Char("Midtrans Server Key")
    midtrans_mode = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production'),
    ], default='sandbox')

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'midtrans.client_key', self.midtrans_client_key)
        self.env['ir.config_parameter'].sudo().set_param(
            'midtrans.server_key', self.midtrans_server_key)
        self.env['ir.config_parameter'].sudo().set_param(
            'midtrans.mode', self.midtrans_mode)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            midtrans_client_key=self.env['ir.config_parameter'].sudo().get_param('midtrans.client_key'),
            midtrans_server_key=self.env['ir.config_parameter'].sudo().get_param('midtrans.server_key'),
            midtrans_mode=self.env['ir.config_parameter'].sudo().get_param('midtrans.mode', 'sandbox'),
        )
        return res
