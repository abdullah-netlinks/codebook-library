# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LibraryBook(models.Model):
    _name = 'library.book.copy'
    _inherit = 'library.book'
    _description = "Library Book's Copy" 

