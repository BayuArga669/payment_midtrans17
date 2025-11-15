import requests
from odoo import http
from odoo.http import request

class MidtransController(http.Controller):

    @http.route('/midtrans/get_token', auth='public', type='json', methods=['POST'], csrf=False)
    def get_token(self):
        server_key = request.env['ir.config_parameter'].sudo().get_param("payment_midtrans.server_key")

        order_id = request.jsonrequest.get('order_id')
        gross_amount = request.jsonrequest.get('amount')

        res = requests.post(
            "https://app.sandbox.midtrans.com/snap/v1/transactions",
            auth=(server_key, ''),
            json={
                "transaction_details": {
                    "order_id": order_id,
                    "gross_amount": gross_amount
                }
            }
        )

        return res.json()
