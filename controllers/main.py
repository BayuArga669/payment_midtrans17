import logging
import json
import hashlib
import pprint

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MidtransController(http.Controller):

    @http.route(
        '/payment/midtrans/notification',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
        save_session=False
    )
    def midtrans_notification(self):
        """Webhook untuk menerima notifikasi dari Midtrans."""
        data = request.jsonrequest
        _logger.info("=" * 80)
        _logger.info("Midtrans notification received:")
        _logger.info(pprint.pformat(data))
        _logger.info("=" * 80)

        # Verifikasi signature
        if not self._verify_signature(data):
            _logger.warning("Invalid Midtrans signature")
            return {'status': 'error', 'message': 'Invalid signature'}

        # Proses notifikasi
        try:
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'midtrans', data
            )
            tx_sudo._process_notification_data(data)
            tx_sudo._handle_notification_data('midtrans', data)
            
            _logger.info(f"Notification processed successfully for {tx_sudo.reference}")
            return {'status': 'ok'}
        except ValidationError as e:
            _logger.error(f"Validation error processing Midtrans notification: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            _logger.exception("Unexpected error processing Midtrans notification")
            return {'status': 'error', 'message': 'Internal server error'}

    @http.route(
        '/payment/midtrans/return',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        save_session=False
    )
    def midtrans_return(self, **kwargs):
        """Halaman return setelah pembayaran."""
        _logger.info("Midtrans return with data: %s", pprint.pformat(kwargs))
        
        order_id = kwargs.get('order_id')
        
        if order_id:
            tx_sudo = request.env['payment.transaction'].sudo().search([
                ('reference', '=', order_id),
                ('provider_code', '=', 'midtrans')
            ], limit=1)
            
            if tx_sudo:
                # Redirect ke halaman status pembayaran
                return request.redirect('/payment/status')
        
        # Jika tidak ada order_id atau transaksi tidak ditemukan
        return request.redirect('/shop/payment')

    def _verify_signature(self, data):
        """Verifikasi signature dari Midtrans."""
        try:
            order_id = data.get('order_id')
            status_code = data.get('status_code')
            gross_amount = data.get('gross_amount')
            signature_key = data.get('signature_key')

            if not all([order_id, status_code, gross_amount, signature_key]):
                _logger.warning("Missing required fields for signature verification")
                return False

            tx_sudo = request.env['payment.transaction'].sudo().search([
                ('reference', '=', order_id),
                ('provider_code', '=', 'midtrans')
            ], limit=1)

            if not tx_sudo:
                _logger.warning(f"Transaction not found for order_id: {order_id}")
                return False

            server_key = tx_sudo.provider_id.midtrans_server_key
            
            # Format gross_amount to ensure it matches Midtrans format
            if isinstance(gross_amount, str):
                gross_amount = gross_amount.split('.')[0]  # Remove decimals if any
            
            signature_string = f"{order_id}{status_code}{gross_amount}{server_key}"
            calculated_signature = hashlib.sha512(signature_string.encode()).hexdigest()

            is_valid = calculated_signature == signature_key
            
            if not is_valid:
                _logger.warning(
                    f"Signature mismatch for {order_id}. "
                    f"Expected: {calculated_signature}, Got: {signature_key}"
                )
            
            return is_valid
            
        except Exception as e:
            _logger.exception("Error verifying signature")
            return False
