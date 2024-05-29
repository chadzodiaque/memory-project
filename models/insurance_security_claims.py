from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class InsuranceClaims(models.Model):
    _name = "insurance.security.claims"
    _description = "Réclamation d'une assurance"

    name = fields.Char(string='Numéro de réclamation', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Html("Descritption", copy=False,  help='Détails de réclamation')
    date_claims = fields.Date(
        string='Date de réclamations', 
        required=True,
        readonly=True,
        default=fields.Datetime.today()
    )

    state = fields.Selection(
        selection=[
            ("progress", "En cours de traitement"),
            ("validated", "Acceptée"),
            ("refused", "Refusée"),
            ("sold", "Soldée")
        ],
        string="Status",
        required=True,
        copy=False,
        default="progress",
    )
    proofs = fields.Many2many(
        'ir.attachment', 
        string='Preuve de réclamation en appui', 
        help='Veuillez insérer les preuves de votre incidence ainsi que tous les autres documents pour que votre réclamations soit validée',
        readonly=True
    )

    """  Relations de models """
    client_id = fields.Many2one(related='policy_id.client_id', string='Client', readonly=True)
    client_name = fields.Char( related='client_id.name', string="Nom du client", copy=False, readonly=True)
    client_phone = fields.Char( related='client_id.phone', string="Numéro de téléphone", copy=False, readonly=True)
    client_email = fields.Char( related='client_id.email', string="Email", copy=False, readonly=True)

    policy_id = fields.Many2one("insurance.security.policy", string = "Police d'assurance associé")
    policy_name = fields.Char( related='policy_id.name', string="Nom du produit", required=True, copy=False, readonly=True)
    policy_start_date = fields.Date( related='policy_id.start_date', string="Type d'assurance", copy=False, readonly=True)
    policy_end_date = fields.Date( related='policy_id.end_date', string="Type de couvrement", copy=False, readonly=True)
    policy_product_name = fields.Char(related='policy_id.product_name', string="Devise", copy=False, readonly=True)
    currency_id = fields.Many2one(related='policy_id.currency_id', string="Devise", copy=False, readonly=True)
    amount = fields.Float( related='policy_id.product_amount_guarantee', string="Montant garantie", copy=False, readonly=True)

    agent_name = fields.Char( related='policy_id.agent_name', string="Nom du l'agent", required=True, copy=False, readonly=True)
    agent_phone = fields.Char( related='policy_id.agent_phone', string="Numéro de téléphone", required=True, copy=False, readonly=True)
    agent_email = fields.Char( related='policy_id.agent_email', string="Email", required=True, copy=False, readonly=True)

    def validated_claims(self):
        self.state = 'validated'

    def refused_claims(self):
        self.state = 'refused' 

    def sold_claims(self):
        self.write({"state": "sold"})

        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        # Another way to get the journal:
        # journal = self.env["account.move"].with_context(default_move_type="out_invoice")._get_default_journal()
        for prop in self:
            self.env["account.move"].create(
                {
                    "partner_id": prop.client_id.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": prop.name,
                                "quantity": 1.0,
                                "price_unit": prop.amount,
                            },
                        ),
                    ],
                }
            )
        


    @api.model
    def create(self, values):
        rtn = super().create(values)
        if rtn.name == 'New':
            rtn.name = self.env['ir.sequence'].next_by_code('claims.details') or 'New'
        rtn.state = "progress"
        return rtn

    


    