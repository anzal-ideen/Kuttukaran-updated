{
    'name': 'bidding',
    'version': '1.0.0',
    'category': 'bidding',
    'author': 'ideenkreise',
    'sequence': -100,
    'summary': 'bidding management system',
    'description': """bidding management system""",
    'depends': ['base', 'account', 'hr', 'stock', 'purchase', 'base_accounting_kit', 'product_purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'wizard/add_to_bidding.xml',
        'views/tenders_inherit_view.xml',
        'views/bid_request.xml',

        'views/create_bidding.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
