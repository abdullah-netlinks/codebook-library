# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, exceptions
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _

logger = logging.getLogger(__name__)


class BaseArchive(models.AbstractModel):
    _name = 'base.archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active
  
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    # _order = 'date_release desc, name'
    _inherit = ['base.archive']
    # _rec_name = 'short_name'

    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many('res.partner', string='Authors')
    # short_name = fields.Char('Short Title', required=True)
    short_name = fields.Char('Short Title',translate=True, index=True)
    isbn = fields.Char('ISBN')
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Unavailable'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')],
        'State',default="draft")
    description = fields.Html('Description',sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    # pages = fields.Integer('Number of Pages')
    pages = fields.Integer('Number of Pages',
        groups='base.group_user',
        states={'lost': [('readonly', True)]},
        help='Total book page count', company_dependent=False)
    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4), # Optional precision decimals,
        )
    cost_price = fields.Float('Book Cost', digits='Book Price')
    retail_price = fields.Monetary('Retail Price', #currency_field='book_currency_id'
    )
    currency_id = fields.Many2one('res.currency', string='Currency')
    publisher_id = fields.Many2one(
        'res.partner', 
        string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[])
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        # readonly=True
    )
    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string = "Days Since Release",
        compute = '_compute_age',
        inverse = '_inverse_age',
        search = '_search_age',
        store = False,
        compute_sudo = True
    )
    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string="Reference Document"
    )
    manager_remarks = fields.Text('Manager Remarks')
    old_edition = fields.Many2one('library.book', string='Old Edition')

    def get_xml(self):
        book = self.env.ref('my_library.book_cookbook1')
        print('book')

    def grouped_data(self):
        data = self._get_average_cost()
        print(data)
        # _logger.info("Groupped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', "!=", False)], # Domain
            ['category_id', 'cost_price:avg'], # Fields to access
            ['category_id'] # group_by
            )
        return grouped_result
    
    # Sorting recordset
    def sort_books(self):
        all_books = self.search([])
        print(all_books)
        books_sorted = self.sort_books_by_date(all_books)
        # logger.info('Books before sorting: %s', all_books)
        # logger.info('Books after sorting: %s', books_sorted)

    # @api.model
    # def create(self, values):
    #     if not self.user_has_groups('my_library.group_librarian'):
    #         if values['manager_remarks']:
    #             raise UserError(
    #                 "You are not allowed to add a value in 'manager_remarks'"
    #             )
    #     return super(LibraryBook, self).create(values)

    # @api.model YOU CAN'T USE API.MODEL HERE AS IT WILL PASS AN ADDITIONAL PARAMETER AND THUS AN ERROR
    
    def write(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                del values['manager_remarks']
                # raise UserError(
                #     'You are not allowed to edit '
                #     'manager_remarks'
                # )
        return super(LibraryBook, self).write(values)


    # def unlink(self):
    #     print('running unlink extended')
    #     if not self.user_has_groups('my_library.group_librarian'):
    #         print('user doesnot have group')
    #         raise UserError(
    #                     'You cannot delete books'
    #                 ) # This popup will prevent the function from further proceeding
    #                   # to calling the super unlink method
    #     else:
    #         print('user has group')
    #     return super(LibraryBook, self).unlink()

    


    @api.model
    def sort_books_by_date(self, all_books):
        print('running the sorting method now ..')
        return all_books.sorted(key='date_release')

    # TRAVERSING RECORDSETS: creating a dataset from attributes of a model
    def list_author_names(self):
        all_books = self.search([])
        author_names = self.get_author_names(all_books)
        print(author_names)

    
    @api.model
    def get_author_names(self, books):
        return books.mapped('author_ids.name')



    # FILTERING RECORDSETS    
    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        print(len(filtered_books))
    
    @api.model
    def books_with_multiple_authors(self, all_books):

        def predicate(book):
            # if len(book.author_ids) > 1:
            if len(book.author_ids) > 1:
                return True
        return all_books.filter(predicate)

        

    # SEARCHING:
    """ just a search function with a custom domain. results of the search
    were logged in the server. we hardcoded the search domain just to see
    how it works """
    def find_book(self):
        domain = [
            '|',
                '|', ('name','ilike','Essentials'),
                     ('category_id.name','ilike','Category Name'),
                '|', ('name','ilike','Java'),
                     ('category_id.name','ilike','Category Name 2'),
 
        ]

        books = self.search(domain)
        for book in books:
            print(book.name)
 



    # UPDATING RECORDSETS
    def change_release_date(self):
        # self.ensure_one()
        # for book in self:
        self.update({
            'date_release': fields.Date.today()
        })
        self.date_release = fields.Date.today()
        print (f'Updated date for record {self.id}')


    #SEARCHING OUTSIDE CURRENT MODEL
    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        for member in all_members:
            print("Member:", member)
        return True

    def fetch_partners(self):
        partner_model = self.env['res.partner']
        inactive_partners = partner_model.search([('active','=',True)])
        print(len(inactive_partners))
            # result is 38
        active_partners = partner_model.search([('active','=',True)])
        print(len(active_partners))
            # result is 5
        all_partners = active_partners + inactive_partners
        print(len(all_partners))
            # result is 43

        # for partner in active_partners:
        #     print(partner.name) 
        return True

    #UPDATING STATUS AND ACTIONS
    @api.model
    def _is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('draft','available'),
            ('available','borrowed'),
            ('borrowed','available'),
            ('available','lost'),
            ('borrowed','lost'),
            ('lost','available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book._is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        print('running parent function ..')
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name','=','message_ids')
        ])
        return [(x.model, x.name) for x in models]

    
    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|', '|',
                ('name', operator, name),
                ('isbn', operator, name),
                ('author_ids.name', operator, name)
            ]
        return super(LibraryBook, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)


    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = [] if args is None else args.copy()
    #     if not(name == '' and operator == 'ilike'):
    #         args += ['|', '|',
    #         ('name', operator, name),
    #         ('isbn', operator, name),
    #         ('author_ids.name', operator, name)
    #         ]
    #     return super(LibraryBook, self)._name_search(name=name, args=args, operator=operator,
    #                                                 limit=limit, name_get_uid=name_get_uid)




    # def _name_search(self, name='', args=None, operator='ilike',limit=100, name_get_uid=None):
    #     args = [] if args is None else args.copy()
    #     if not (name == '' and operator == 'ilike'):
    #         args += ['|',
    #                     '|',
    #                         ('name', operator, name),
    #                         ('isbn', operator, name),
    #                         ('author_ids.name', operator, name),            
    #                     ]
    #     return super(LibraryBook, self)._name_search(
    #         name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
    #     )


        # result = []
        # for record in self:
        #     rec_name = "%s [%s]" % (record.name, record.date_release)
        #     result.append((record.id, rec_name))
        # return result

    # APPLYING CONSTRAINTS
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError(
                    'Release date must be in the past')

    _sql_constraints = [
            ('name_uniq', 'UNIQUE (name)',
            'Book title must be unique.'),
            ('positive_page', 'CHECK(pages>=0)',
            'No of pages must be positive')
        ]

    # CREATING COMPUTED FIELDS
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days = value)
        value_date = today - value_days
        # convert the operator
        # book with age > value have a date < value date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'
    
    # published_book_ids = fields.One2many(
    #     'library.book', 'publisher_id',
    #     string='Published Books')

    authored_book_ids = fields.Many2many(
        'library.book', string='Authored Books',
        # relation='library_book_res_partner_rel' #optional
    )
    count_books = fields.Integer(
        'Number of Authored Books', 
        compute='_compute_count_books'
        )
    
    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

    
class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    
    partner_id = fields.Many2one(
        'res.partner',
        ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')


