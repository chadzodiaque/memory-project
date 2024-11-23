from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

from ..utils.cryptofpe import Crypto
import logging

_logger = logging.getLogger(__name__)

class InsuranceDemand(models.Model):

    _name = "insurance.security.demand"
    _description = "Demande de police d'assurance"

    name = fields.Char("Titre de la demande", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Html("Descritption de la demande", copy=False, help='Détails de votre demande. Préciser le produit d\'assurance que vous souhaité', readonly=True)
    state = fields.Selection(
        selection=[
            ("accepted", "Acceptée"),
            ("refused", "Refusée"),
            ("progress", "En cours"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="progress",

    )
    date_demand = fields.Date(
        string='Date de demande', 
        required=True,
        default=fields.Datetime.today(),
        readonly=True
    )

    client_id = fields.Many2one("res.partner", string = "Client", readonly=True)
    client_name = fields.Char( related='client_id.name', string="Nom du client", copy=False, readonly=True)
    client_phone = fields.Char( related='client_id.phone', string="Numéro de téléphone", copy=False, readonly=True)
    client_email = fields.Char( related='client_id.email', string="Email", copy=False, readonly=True)

    cars_number = fields.Integer(string="Nombre de véhicules", readonly=True, copy=False)
    
    proofs = fields.Many2many(
        'ir.attachment', 
        string='Preuves ', 
        help=' Insérer les documents suivants : Carte d\'identité ou passport, Carte grise(s), Permis de conduire, TVM et Attestion de controle technique',
        readonly=True
    )

    
    def action_open_attachments(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.attachments.ids)],
            'context': "{'create': False}"
        }
    
    def validated_demand(self):
        self.state = 'accepted'

    def refused_demand(self):
        self.state = 'refused'
    
    @api.constrains('cars_number')
    def _check_cars_number(self):
        for record in self:
            if record.cars_number < 1:
                raise ValidationError("Le nombre de véhicules doit être superieur à 0")
    
    def action_send_email(self):
        mail_template = self.env.ref('insurance_security.insurance_security_demand_email_template')
        mail_template.send_mail(self.id, force_send=True)

    @api.model
    def create(self, values):
        rtn = super().create(values)
        if rtn.name == 'New':
            rtn.name = self.env['ir.sequence'].next_by_code('demand.details') or 'New'
        rtn.state = "progress"
        rtn.client_id = self.env.user.partner_id
        return rtn 
    
    