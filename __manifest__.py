{
    'name': 'Payment Midtrans for Odoo 17',
    'version': '1.0',
    'summary': 'Integrasi Midtrans Payment Gateway dengan Odoo 17',
    'author': 'Bayu',
    'category': 'Accounting/Payment',
    'depends': [
        'payment',
        'website_sale',
    ],
    'data': [
        'views/payment_midtrans_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_midtrans17/static/src/js/midtrans.js',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
