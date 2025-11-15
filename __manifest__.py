# -*- coding: utf-8 -*-
{
    'name': 'Midtrans Payment Gateway',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Integrasi Midtrans Payment Gateway untuk Odoo E-commerce',
    'description': """
        Midtrans Payment Gateway Integration
        =====================================
        
        Modul ini mengintegrasikan Midtrans sebagai payment gateway untuk Odoo E-commerce.
        
        Fitur:
        ------
        * Pembayaran dengan Snap Midtrans
        * Dukungan berbagai metode pembayaran (Credit Card, Bank Transfer, E-Wallet, dll)
        * Notifikasi otomatis untuk status pembayaran
        * Sandbox dan Production mode
        * Verifikasi signature untuk keamanan
        
        Konfigurasi:
        -----------
        1. Dapatkan credentials dari dashboard Midtrans
        2. Aktifkan payment provider di Odoo
        3. Masukkan Merchant ID, Client Key, dan Server Key
        4. Pilih mode Test atau Production
        5. Daftarkan webhook URL di Midtrans dashboard
    """,
    'author': 'Bayu Arga Pratama Rinaldi',
    'website': 'https://www.yourcompany.com',
    'depends': ['payment', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_midtrans_templates.xml',
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
