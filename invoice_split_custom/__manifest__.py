# -*- coding: utf-8 -*-
{
    'name': "Invoice Split Based on Product Category",
    'version': '1.0',
    'summary': """Create Separate Invoices Based On Product Categories""",
    'description': """
    With this module, We can Split and Print Separate Invoices Based on Product Categories.""",
    "author": "Ideenkreise Tech Pvt Ltd",
    'website': 'https://ideenkreisetech.com/',
    'category': 'Stock',
    'depends': ['product', 'stock', 'stock_account'],
    'data': [
	'data/cron_sync_oracle.xml',
	'security/ir.model.access.csv',
        'wizard/report_split_wizard.xml',
        'report/report_split_invoice.xml',
'report/report_invoice.xml',
	'views/splited_invoice_views.xml',
    'views/product_template_views.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
