{''
 'name': 'Lease Management',
 'summary': """Custom for ERP""",
 'version': '0.1',
 'sequence':'-999999',
 'description': """Lease/Rental Management System""",
 'author': 'Ideenkreise Tech Pvt Ltd',
 'company': 'Ideenkreise Tech Pvt Ltd',
 'website': 'https://www.ideenkreisetech.com',
 'category': 'Tools',
  'depends': ['account','sale','purchase','stock','product_purchase','base'],
 'license': 'AGPL-3',
 'data': [

  'security/ir.model.access.csv',
  'security/group.xml',

  'views/lms.xml',
  'views/po_workflow.xml',
  'views/masters.xml',
  'views/reports.xml',
  'data/sequence.xml',
  'data/cron.xml',

 ],
 'demo': ['demo/demo.xml'],
 'installable': True,
 'auto_install': False,
 'application' : True
 }
