import logging
import requests
import base64
import json
from werkzeug import urls

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    midtrans_order_id = fields.Char(
        string='Midtrans Order ID',
        readonly=True
    )
    midtrans_snap_token = fields.Char(
        string='Snap Token',
        readonly=True
    )
    midtrans_transaction_id = fields.Char(
        string='Transaction ID',
        readonly=True
    )

    def _get_specific_rendering_values(self, processing_values):
        """Override untuk menambahkan values spesifik Midtrans."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'midtrans':
            return res

        # Siapkan payload untuk Midtrans Snap
        payload = self._midtrans_prepare_payment_request_payload()
        
        # Request Snap Token dari Midtrans
        snap_token = self._midtrans_get_snap_token(payload)
        
        if snap_token:
            self.midtrans_snap_token = snap_token
            self.midtrans_order_id = payload['transaction_details']['order_id']
            
            urls = self.provider_id._get_midtrans_urls()
            res.update({
                'snap_token': snap_token,
                'client_key': self.provider_id.midtrans_client_key,
                'snap_js_url': urls['snap_js'],
                'api_url': self.provider_id.get_base_url(),
            })
        
        return res

    def _midtrans_prepare_payment_request_payload(self):
        """Siapkan payload untuk request Snap Token."""
        self.ensure_one()
        
        base_url = self.provider_id.get_base_url()
        
        return {
            'transaction_details': {
                'order_id': f"{self.reference}",
                'gross_amount': int(self.amount)
            },
            'customer_details': {
                'first_name': self.partner_name or self.partner_id.name or 'Guest',
                'email': self.partner_email or self.partner_id.email or '',
                'phone': self.partner_phone or self.partner_id.phone or '',
            },
            'callbacks': {
                'finish': urls.url_join(base_url, '/payment/midtrans/return'),
                'error': urls.url_join(base_url, '/payment/midtrans/return'),
                'pending': urls.url_join(base_url, '/payment/midtrans/return')
            }
        }

    def _midtrans_get_snap_token(self, payload):
        """Request Snap Token dari Midtrans API."""
        self.ensure_one()
        
        urls = self.provider_id._get_midtrans_urls()
        server_key = self.provider_id.midtrans_server_key
        
        # Encode server key untuk Basic Auth
        auth_string = base64.b64encode(f"{server_key}:".encode()).decode()
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_string}'
        }
        
        try:
            _logger.info(f"Requesting Snap Token for order: {payload['transaction_details']['order_id']}")
            response = requests.post(
                urls['snap_url'],
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            _logger.info(f"Snap Token received successfully")
            return result.get('token')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error getting Midtrans Snap token: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                _logger.error(f"Response content: {e.response.text}")
            raise ValidationError(
                _("Tidak dapat terhubung ke Midtrans. Silakan periksa konfigurasi atau coba lagi nanti.")
            )

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override untuk menangani notifikasi dari Midtrans."""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'midtrans' or len(tx) == 1:
            return tx

        order_id = notification_data.get('order_id')
        if not order_id:
            raise ValidationError(_("Midtrans: Order ID tidak ditemukan dalam notifikasi"))

        tx = self.search([
            ('reference', '=', order_id),
            ('provider_code', '=', 'midtrans')
        ], limit=1)
        
        if not tx:
            raise ValidationError(
                _("Midtrans: Transaksi tidak ditemukan untuk order_id %s") % order_id
            )
        return tx

    def _process_notification_data(self, notification_data):
        """Proses data notifikasi dari Midtrans."""
        super()._process_notification_data(notification_data)
        if self.provider_code != 'midtrans':
            return

        # Update transaction ID
        if notification_data.get('transaction_id'):
            self.midtrans_transaction_id = notification_data['transaction_id']

        transaction_status = notification_data.get('transaction_status')
        fraud_status = notification_data.get('fraud_status', 'accept')

        _logger.info(
            f"Processing Midtrans notification for {self.reference}: "
            f"status={transaction_status}, fraud={fraud_status}"
        )

        if transaction_status == 'capture':
            if fraud_status == 'accept':
                self._set_done()
            elif fraud_status == 'challenge':
                self._set_pending(
                    state_message=_("Pembayaran sedang dalam review fraud detection")
                )
            else:
                self._set_canceled(
                    state_message=_("Pembayaran ditolak oleh fraud detection")
                )
        elif transaction_status == 'settlement':
            self._set_done()
        elif transaction_status in ['cancel', 'deny', 'expire']:
            self._set_canceled(
                state_message=_("Pembayaran %s") % transaction_status
            )
        elif transaction_status == 'pending':
            self._set_pending(
                state_message=_("Menunggu pembayaran")
            )
        else:
            _logger.warning(f"Unknown transaction status: {transaction_status}")

