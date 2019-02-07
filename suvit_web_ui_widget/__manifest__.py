{
    'name': 'Сувит. Виджеты',
    'category': 'UI',
    'summary': 'Модель Виджета для Odoo',
    'website': 'https://suvit.ru',
    'author': 'Suvit LLC',
    'version': '1.0',
    'description': """
Модель Виджета для Odoo
========================
Дерево виджетов

        """,
    'depends': [
        # 'web_widget_text_markdown',  # oca/web
        'suvit_multi_model_tree',  # for widget tree
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/widget_type.xml',
        'views/widget_type_tree.xml',
        'views/suvit_web_ui_widget.xml',
        'views/suvit_web_ui_widget_card.xml',
        'views/suvit_web_ui_widget_features_group.xml',
        'views/menu.xml',
    ],
    'installable': True,
    # 'auto_install': True,
}
