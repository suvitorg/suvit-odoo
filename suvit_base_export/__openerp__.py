{
    'name': 'SUVIT. Ограничение доступа к ir.exports',
    'category': 'suvit',
    'summary': 'Odoo SЭкспорт',
    'version': '1.0',
    'description': """
Odoo Экспорт
=============================

        """,
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',

        'views/ir_exports.xml'
    ],
    'installable': True,
    'auto_install': False,
}
