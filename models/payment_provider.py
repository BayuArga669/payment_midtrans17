# ============================================
# FILE: models/payment_provider.py
# ============================================
import logging
import requests
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('midtrans', 'Midtrans')],
        ondelete={'midtrans': 'set default'}
    )
    
    midtrans_client_key = fields.Char(
        string='Client Key',
        required_if_provider='midtrans',
        groups='base.group_system',
        help='Your Midtrans Client Key from Dashboard'
    )
    
    midtrans_server_key = fields.Char(
        string='Server Key',
        required_if_provider='midtrans',
        groups='base.group_system',
        help='Your Midtrans Server Key from Dashboard'
    )
    
    midtrans_merchant_id = fields.Char(
        string='Merchant ID',
        groups='base.group_system',
        help='Optional: Your Midtrans Merchant ID'
    )

    def _midtrans_get_api_url(self):
        """Return Midtrans API URL based on state (enabled/test)."""
        self.ensure_one()
        if self.state == 'test':
            return 'https://app.sandbox.midtrans.com/snap/v1'
        return 'https://app.midtrans.com/snap/v1'

    def _midtrans_make_request(self, endpoint, data=None, method='POST'):
        """Make request to Midtrans API."""
        self.ensure_one()
        
        url = f"{self._midtrans_get_api_url()}/{endpoint}"
        
        auth = (self.midtrans_server_key, '')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, auth=auth, headers=headers, timeout=10)
            else:
                response = requests.get(url, auth=auth, headers=headers, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error('Midtrans API Error: %s', str(e))
            raise ValidationError(_('Error connecting to Midtrans: %s') % str(e))
