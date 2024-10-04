from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class InsuranceCars(models.Model):
    _name = "insurance.security.cars"
    _description = "Voitures enregistrés"

    
    name = fields.Char(string='Identifiant de la voiture', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    brands = fields.Char(string='Marques du véhicule', required=True, copy=False)
    model = fields.Char(string='Modèle du véhicule', required=True, copy=False)
    serial = fields.Char(string='Numéro de série', required=True, copy=False)
    registration = fields.Char(string='Immatriculation', required=True, copy=False)
    fuel = fields.Selection(
        [
            ('essence', 'Essence'), 
            ('diesel', 'Diesel'), 
            ('electrique', 'Electrique')
        ],
        required=True, 
        default='essence')
    power = fields.Integer(string='Puissance du véhicule', required=True, copy=False)
    cylinder = fields.Integer(string='Nombre de cylindre', required=True, copy=False)
    body = fields.Char(string='Carrosserie du véhicule', required=True, copy=False)
    client_id = fields.Many2one("insurance.security.clients", string = "Client ")
    client_name = fields.Char( related='client_id.name', string="Nom du client", required=True, copy=False, readonly=True)

    @api.constrains('power')
    def _check_power(self):
        for rec in self:
            if rec.power < 0 and rec.power == 0:
                raise ValidationError("La puissance du véhicle ne peut pas être négative")
            
    @api.constrains('cylinder')
    def _check_cylinder(self):
        for rec in self:     
            if rec.cylinder < 0 and rec.cylinder == 0:
                raise ValidationError("Le nombre de cylindre ne peut pas être négative")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('car.details') or 'New'
        return super(InsuranceCars, self).create(vals)
    
    