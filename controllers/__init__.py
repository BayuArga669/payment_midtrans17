# ============================================
# FILE: controllers/__init__.py
# ============================================
from . import main

# ============================================
# FILE: controllers/main.py
# ============================================
import logging
import pprint
import hmac
import hashlib

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class MidtransController(http.Controller):

    @http.route('/payment/midtrans/return', type='http', auth='public', csrf=False)
    def midtrans_return(self, **kwargs):
        """Handle return from Midtrans payment page."""
        _logger.info('Midtrans return with data:\n%s', pprint.pformat(kwargs))
        
        # Redirect to payment status page
        return request.redirect('/payment/status')

    @http.route('/payment/midtrans/webhook', type='json', auth='public', csrf=False)
    def midtrans_webhook(self, **kwargs):
        """Handle Midtrans notification/webhook."""
        data = request.get_json_data()
        _logger.info('Midtrans webhook received:\n%s', pprint.pformat(data))

        try:
            # Verify signature
            order_id = data.get('order_id')
            status_code = data.get('status_code')
            gross_amount = data.get('gross_amount')
            signature_key = data.get('signature_key')
            
            # Find transaction
            tx_sudo = request.env['payment.transaction'].sudo().search([
                ('midtrans_order_id', '=', order_id)
            ], limit=1)
            
            if not tx_sudo:
                _logger.warning('No transaction found for order_id: %s', order_id)
                return {'status': 'error', 'message': 'Transaction not found'}
            
            # Verify signature
            server_key = tx_sudo.provider_id.midtrans_server_key
            calculated_signature = hashlib.sha512(
                f"{order_id}{status_code}{gross_amount}{server_key}".encode()
            ).hexdigest()
            
            if calculated_signature != signature_key:
                _logger.warning('Invalid signature for order_id: %s', order_id)
                return {'status': 'error', 'message': 'Invalid signature'}
            
            # Process notification
            tx_sudo._process_notification_data(data)
            
            return {'status': 'success'}
            
        except Exception as e:
            _logger.exception('Error processing Midtrans webhook: %s', str(e))
            return {'status': 'error', 'message': str(e)}
