from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BookCategory(models.Model):
    _name = 'library.book.category'
    _parent_store = True
    _parent_name = "parent_id" # optional if field is 'parent_id'

    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one(
        'library.book.category',
        string='Parent Category',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many(
        'library.book.category', 'parent_id',
        string='Child Categories')
    
    parent_path = fields.Char(index=True)
    


    def create_categories(self):
        categ1 = {
            'name': 'Children Bed Time Stories',
            'description': 'Books with illustrations for kids'
        }
        categ2 = {
            'name': 'Agatha Cristy Novels',
            'description': 'Agatha Cristy Novels for Crime and Murder cases'
        }
        parent_category_val = {
            'name': 'XXFiction Novels [Parent Category]',
            'description': 'XXAll types of Fiction Novels and Books',
            'child_ids': [
                (0, 0, categ1), # 0, 0 is used when you want a record to belong to a parent record.
                (0, 0, categ2)
            ]
        }
        # THREE APPROACHES TO CREATE: 
        # APPROACH 1: 
        record = self.env['library.book.category'].create(parent_category_val)
        
        # APPROACH 2:
        # Instead of the above, I could also directly use the code below by providing the values 
        # directly as a dictionary inside the create method:

        # record = self.env['library.book.category'].create({
        #     'name': 'YYFiction Novels [Parent Category]',
        #     'description': 'YY All types of Fiction Novels and Books'})

        # APPROACH 3:
        # we can also create multiple records by passing in the variables with the values like:
        # muliple_records = self.env['library.book.category'].create([categ1, categ2])


    # @api.constraints('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')