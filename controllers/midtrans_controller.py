from odoo import http
from odoo.http import request

class MidtransController(http.Controller):

    @http.route('/payment/midtrans/callback', type='json', auth='public', csrf=False)
    def midtrans_callback(self, **payload):
        # proses pembayaran diterima Midtrans
        tx = request.env['payment.transaction'].sudo()
        tx.form_feedback(payload, 'midtrans')
        return {'status': 'ok'}
