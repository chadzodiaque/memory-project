from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

class InsuranceProduct(models.Model):

    _name = "insurance.security.product"
    _description = "Produit d'assurance"

    name = fields.Char("Nom du produit", required=True, copy=False)
    image = fields.Image(max_width=1024, max_height=1024)
    currency_id = fields.Many2one("res.currency", string="Devise", required=True)
    prime_price= fields.Float("Prime d'assurrance ", required=True, copy=False, help=' Montant d\'argent que le client paie à la compagnie d\'assurance pour obtenir une couverture d\'assurance.')
    amount_guarantee = fields.Float("Montant garantie", required=True, copy=False, help='Montant maximal que la compagnie d\'assurance versera en cas de survenance d\'un événement au client ')
    advantages = fields.Html("Avantages et exclusions", copy=False, required=True)
    conditions = fields.Html("Conditions et modalités", copy=False, required=True)
    options = fields.Html("Options de personnalisation", copy=False, required=True, help='options de personnalisation permettant aux assurés de choisir les niveaux de couverture, les franchises, les options facultatives, etc., en fonction de leurs besoins spécifiques.')
    coverage_type = fields.Selection(
        [
            ('individual', 'Individual'), 
            ('family', 'Family'), 
            ('group', 'Group')
        ],
        required=True, 
        default='individual')
    creation_date = fields.Date("Date de creation", default=fields.Datetime.today(), required=True, copy=False, readonly=True)


    """ Relations de champ """
    type_ids = fields.Many2many("insurance.security.type", string= "Types")

    @api.constrains('amount_guarantee')
    def _check_amount_guarantee(self):
        for record in self:
            if float_is_zero(record.amount_guarantee, precision_rounding=0.01) or record.amount_guarantee < 0:
                raise ValidationError(
                    "Le prix du montant ne doit pas être nulle ou négatif")

    @api.constrains('prime_price')
    def _check_prime_price(self):
        for record in self:
            if float_is_zero(record.prime_price, precision_rounding=0.01) or record.prime_price < 0:
                raise ValidationError(
                    "Le prix de la prime ne doit pas être nulle ou négatif")
            