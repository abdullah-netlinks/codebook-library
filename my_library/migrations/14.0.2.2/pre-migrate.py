# # -*- coding: utf-8 -*-

# # NOTE: This is just for demo purpose
# # This function invoked only if system already have 14.0.0 version installed
# def migrate(cr, version):
#     # print('running the pre-migration script .....................')
#     print('Pre-migration Script running .....................')
#     cr.execute("""
#         ALTER TABLE library_book
#         RENAME COLUMN date_release_char TO date_release""")