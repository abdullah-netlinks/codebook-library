# -*- coding: utf-8 -*-
{
    'name': "My Library",  # Module title
    'summary': "Manage books easily",  # Module subtitle phrase
    'description': """
Manage Library
==============
Description related to library.
    """,  # Supports reStructuredText(RST) format
    'author': "Parth Gajjar",
    'website': "http://www.example.com",
    'category': 'Tools',
    'version': '14.0.2.3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        # 'views/library_book.xml',
        'views/library_book_categ.xml',
        'views/library_book_revised.xml',
        'views/library_book_rent.xml',
        'views/res_partner.xml',
        'wizard/library_book_rent_wizard.xml',
        'data/data.xml',
        'data/demo.xml',
    ],
    # 'demo': [
    #     'demo.xml'
    # ],
}