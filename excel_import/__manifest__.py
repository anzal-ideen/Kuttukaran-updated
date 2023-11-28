{''
 'name': 'Excel Import',
 'summary': """Custom for ERP""",
 'version': '0.1',
 'sequence':'-999999',
 'description': """Lease/Rental Management System""",
 'author': 'Ideenkreise Tech Pvt Ltd',
 'company': 'Ideenkreise Tech Pvt Ltd',
 'website': 'https://www.ideenkreisetech.com',
 'category': 'Tools',
  'depends': ['account','report_xlsx'],
 'license': 'AGPL-3',
 'data': [


  'security/ir.model.access.csv',
  # 'security/group.xml',

  'views/view.xml',
  'reports/report.xml'

 ],
 'demo': [],
 'installable': True,
 'auto_install': False,
 'application' : True
 }
