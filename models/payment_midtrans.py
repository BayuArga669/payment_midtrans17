from odoo import models, fields

class ProviderMidtrans(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('midtrans', 'Midtrans')],
        ondelete={'midtrans': 'set default'}
    )

    midtrans_server_key = fields.Char("Midtrans Server Key")
    midtrans_client_key = fields.Char("Midtrans Client Key")

    def _get_midtrans_urls(self):
        return {
            'snap_url': 'https://app.midtrans.com/snap/v1/transactions',
            'sandbox_snap_url': 'https://app.sandbox.midtrans.com/snap/v1/transactions',
        }
