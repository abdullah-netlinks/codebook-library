# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

class LibraryBookRent(models.Model):
    _name = 'library.book.rent'

    book_id = fields.Many2one('library.book','Book', required=True)
    borrower_id = fields.Many2one('res.partner','Borrower',required=True)
    state = fields.Selection([
        ('ongoing','Ongoing'),
        ('returned','Returned'),
        ('lost','Lost')
    ], 'State', default='ongoing', required=True)
    rent_date = fields.Date(default = fields.Date.today, string='Date Rented')
    return_date = fields.Date('Return Date')

    def book_lost(self):
        print('running book_lost function in library.book.rent class ...')
        self.ensure_one()
        self.sudo().state = 'lost'
        book_with_different_context = self.book_id.with_context(avoid_deactivate=True)
        book_with_different_context.sudo().make_lost()
    