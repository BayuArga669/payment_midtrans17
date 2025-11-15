# ============================================
# FILE: models/payment_transaction.py
# ============================================
import logging
import pprint
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    midtrans_order_id = fields.Char(
        string='Midtrans Order ID',
        readonly=True,
        help='Order ID from Midtrans'
    )
    
    midtrans_snap_token = fields.Char(
        string='Snap Token',
        readonly=True,
        help='Snap token for payment popup'
    )

    def _get_specific_rendering_values(self, processing_values):
        """Override to add Midtrans-specific rendering values."""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'midtrans':
            return res

        # Generate order ID
        order_id = f"ORDER-{self.reference}-{fields.Datetime.now().timestamp()}"
        
        # Prepare transaction details
        payload = {
            'transaction_details': {
                'order_id': order_id,
                'gross_amount': int(self.amount),
            },
            'customer_details': {
                'first_name': self.partner_id.name or 'Customer',
                'email': self.partner_id.email or '',
                'phone': self.partner_id.phone or self.partner_id.mobile or '',
            },
            'item_details': self._midtrans_prepare_item_details(),
            'callbacks': {
                'finish': urls.url_join(self.get_base_url(), '/payment/midtrans/return'),
            }
        }

        # Call Midtrans API to get snap token
        try:
            response = self.provider_id._midtrans_make_request('transactions', payload)
            snap_token = response.get('token')
            
            self.write({
                'midtrans_order_id': order_id,
                'midtrans_snap_token': snap_token,
            })
            
            rendering_values = {
                'snap_token': snap_token,
                'client_key': self.provider_id.midtrans_client_key,
                'api_url': self.provider_id._midtrans_get_api_url().replace('/snap/v1', ''),
            }
            
            return rendering_values
            
        except Exception as e:
            _logger.error('Error creating Midtrans transaction: %s', str(e))
            raise ValidationError(_('Unable to create payment transaction. Please try again.'))

    def _midtrans_prepare_item_details(self):
        """Prepare item details for Midtrans."""
        items = []
        
        # If transaction is linked to a sale order
        if self.sale_order_ids:
            for order in self.sale_order_ids:
                for line in order.order_line:
                    items.append({
                        'id': str(line.product_id.id),
                        'name': line.product_id.name,
                        'price': int(line.price_unit),
                        'quantity': int(line.product_uom_qty),
                    })
        else:
            # Generic item
            items.append({
                'id': 'PAYMENT',
                'name': self.reference or 'Payment',
                'price': int(self.amount),
                'quantity': 1,
            })
        
        return items

    @api.model
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override to find transaction from Midtrans notification."""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'midtrans' or len(tx) == 1:
            return tx

        order_id = notification_data.get('order_id')
        if not order_id:
            raise ValidationError('Midtrans: Missing order_id in notification data')

        tx = self.search([('midtrans_order_id', '=', order_id), ('provider_code', '=', 'midtrans')])
        if not tx:
            raise ValidationError(f'Midtrans: No transaction found for order_id {order_id}')

        return tx

    def _process_notification_data(self, notification_data):
        """Process Midtrans notification data."""
        super()._process_notification_data(notification_data)
        if self.provider_code != 'midtrans':
            return

        _logger.info('Processing Midtrans notification for tx %s:\n%s', self.reference, pprint.pformat(notification_data))

        transaction_status = notification_data.get('transaction_status')
        fraud_status = notification_data.get('fraud_status', 'accept')

        if transaction_status == 'capture':
            if fraud_status == 'accept':
                self._set_done()
            elif fraud_status == 'challenge':
                self._set_pending()
        elif transaction_status == 'settlement':
            self._set_done()
        elif transaction_status in ['deny', 'cancel', 'expire']:
            self._set_canceled()
        elif transaction_status == 'pending':
            self._set_pending()
        else:
            _logger.warning('Unhandled Midtrans transaction status: %s', transaction_status)