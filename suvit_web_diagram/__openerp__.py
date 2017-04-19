{
    'name': 'Сувит. Диаграмма',
    'category': 'Website',
    'summary': 'Сохраняемые диаграммы',
    'version': '1.0',
    'description': """
Сохраняемые диаграммы
===========================

* Сохранение позиций вершин в диаграмме

        """,
    'author': 'Suvit LLC',
    'website': 'https://suvit.ru',
    'depends': [
        'web_diagram',
    ],
    'data': [
        'static/data/static_data.xml',
    ],
    'js': [
        "static/src/js/diagram.js",
    ],
    'installable': False,
    'auto_install': False,
}
