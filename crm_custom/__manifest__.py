# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'crm_custom',
    'version': '1.0.0',
    'category': 'CRM custom',
    'author': 'Ideenkreise',
    'sequence': -112,
    'summary': 'crm custom',
    'description': """crm""",
    'depends': ['base', 'stock', 'account'],
    'data': [
        'wizard/share_crm.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/crm_mail.xml',
        'views/crm_form_inherited.xml',
        'views/location_view.xml',
        'views/ideabook_view.xml'
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'assets': {},
    'post_init_hook': '',
    'license': 'LGPL-3',
}
