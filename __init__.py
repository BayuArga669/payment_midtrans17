from . import models
from . import controllers

# ============================================
# FILE: __manifest__.py
# ============================================
{
    'name': 'Payment Provider: Midtrans',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Payment Provider: Midtrans Payment Gateway',
    'description': """
Midtrans Payment Gateway Integration for Odoo 17
=================================================
This module integrates Midtrans payment gateway with Odoo e-commerce.

Features:
---------
* Credit Card payments
* Bank Transfer (Virtual Account)
* E-Wallet (GoPay, OVO, Dana, ShopeePay)
* QRIS payments
* Installment payments
* Real-time payment status updates
* Sandbox and Production modes
* Automatic transaction reconciliation
    """,
    'author': 'Bayu',
    'website': 'https://www.midtrans.com',
    'depends': [
        'payment',
        'website_sale',
    ],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_midtrans_templates.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_midtrans/static/src/js/payment_form.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}