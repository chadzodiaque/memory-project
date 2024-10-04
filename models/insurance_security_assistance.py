from odoo import fields, models, api, _
from ..utils.cryptofpe import Crypto
from odoo.exceptions import ValidationError

class InsuranceAssistance(models.Model):

    _name = "insurance.security.assistance"
    _description = "Traitement d'assistance"

    name = fields.Char("Intitulé de l'assistance", required=True, copy=False)
    description = fields.Html("Description", copy=False, required=True)
    state = fields.Selection(
        selection=[
            ("progress", "En cours de traitement"),
            ("received", "Reçue"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="progress",
    )
    user_id = fields.Many2one("res.partner", string="Utilisateur", copy=False, readonly=True, default = lambda self: self.env.user.partner_id)

    def received_assistance(self):
        self.state = 'received'
    
    