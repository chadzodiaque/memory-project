from odoo import fields, models

class InsuranceAssistance(models.Model):

    _name = "insurance.security.assistance"
    _description = "Traitement d'assistance"

    name = fields.Char("Intitulé de l'assistance", required=True, copy=False, readonly=True)
    email = fields.Char("Email", required=True, copy=False, readonly=True)
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
    creation_date = fields.Date("Date de creation", default=fields.Datetime.today(), required=True, copy=False, readonly=True)

    user_id = fields.Many2one("res.partner", string="Utilisateur", copy=False, readonly=True)

    def received_assistance(self):
        self.state = 'received'
