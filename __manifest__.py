# -*- coding: utf-8 -*-
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
* Credit Card payments (Visa, MasterCard, JCB, Amex)
* Bank Transfer (BCA, Mandiri, BNI, BRI, Permata)
* E-Wallet (GoPay, OVO, Dana, ShopeePay, LinkAja)
* QRIS payments
* Installment payments
* Real-time payment status updates via webhook
* Sandbox and Production modes
* Automatic transaction reconciliation
* Secure payment with Snap popup

Configuration:
--------------
1. Get your credentials from Midtrans Dashboard (https://dashboard.midtrans.com)
2. Go to Settings > Payment Providers > Midtrans
3. Enter your Client Key and Server Key
4. Choose Test or Production mode
5. Publish the provider

Technical:
----------
* Uses Midtrans Snap API
* Webhook support for payment notifications
* SHA512 signature verification
* Support for multiple payment channels
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
}