from odoo import fields, models, api

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('midtrans', 'Midtrans')],
        ondelete={'midtrans': 'set default'}
    )
    midtrans_server_key = fields.Char(
        string='Server Key',
        required_if_provider='midtrans',
        groups='base.group_system',
        help='Server Key dari Midtrans Dashboard'
    )
    midtrans_client_key = fields.Char(
        string='Client Key',
        required_if_provider='midtrans',
        help='Client Key dari Midtrans Dashboard'
    )
    midtrans_merchant_id = fields.Char(
        string='Merchant ID',
        required_if_provider='midtrans',
        help='Merchant ID dari Midtrans Dashboard'
    )

    def _get_midtrans_urls(self):
        """Return the URLs for Midtrans API."""
        self.ensure_one()
        if self.state == 'enabled':
            # Production URLs
            return {
                'snap_url': 'https://app.midtrans.com/snap/v1/transactions',
                'snap_js': 'https://app.midtrans.com/snap/snap.js',
                'api_url': 'https://api.midtrans.com/v2'
            }
        else:  # test mode (disabled or test state)
            # Sandbox URLs
            return {
                'snap_url': 'https://app.sandbox.midtrans.com/snap/v1/transactions',
                'snap_js': 'https://app.sandbox.midtrans.com/snap/snap.js',
                'api_url': 'https://api.sandbox.midtrans.com/v2'
            }

    def _midtrans_get_supported_currencies(self):
        """Return supported currencies."""
        return ['IDR']