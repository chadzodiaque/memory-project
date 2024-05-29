from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class InsurancePayment(models.Model):

    _name = "insurance.security.payments"
    _description = "Versement des primes d'assurance des clients"

    name = fields.Char(string='Numéro de versements', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    currency_id = fields.Many2one("res.currency", string="Devis", required=True)
    amount= fields.Float("Montant versée ", required=True, copy=False, help=' Montant d\'argent que le client verse à la compagnie d\'assurance pour obtenir une couverture d\'assurance.')
    amount_date = fields.Date(string='Date de versement', 
        required=True, 
        default=fields.Datetime.today())
    policy_id = fields.Many2one("insurance.security.policy", string = "Police d'assurance associé", required=True)
    policy_name = fields.Char( related='policy_id.name', string="Nom du produit", required=True, copy=False, readonly=True)
    policy_start_date = fields.Date( related='policy_id.start_date', string="Type d'assurance", copy=False, readonly=True)
    policy_end_date = fields.Date( related='policy_id.end_date', string="Type de couvrement", copy=False, readonly=True)
    policy_product_name = fields.Char(related='policy_id.product_name', string="Devise", copy=False, readonly=True)
    agent_name = fields.Char( related='policy_id.agent_name', string="Nom du l'agent", required=True, copy=False, readonly=True)

    client_id = fields.Many2one("res.partner", string = "Client ", required=True)
    client_name = fields.Char( related='client_id.name', string="Nom du client", copy=False, readonly=True)
    client_phone = fields.Char( related='client_id.phone', string="Numéro de téléphone", copy=False, readonly=True)
    client_email = fields.Char( related='client_id.email', string="Email", copy=False, readonly=True)

    @api.model
    def create(self, values):
        rtn = super().create(values)
        if rtn.name == 'New':
            rtn.name = self.env['ir.sequence'].next_by_code('payments.details') or 'New'
        return rtn
    
    @api.onchange('client_id')
    def onClientChange(self):
        self.policy_id = False

    # Définition du domaine pour le champ policy_id
    @api.onchange('client_id')
    def _onchange_client_id(self):
        if self.client_id:
            return {'domain': {'policy_id': [('client_id', '=', self.client_id.id)]}}
        else:
            return {'domain': {'policy_id': []}}
