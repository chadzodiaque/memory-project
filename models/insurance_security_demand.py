from odoo import fields, models, api, _

class InsuranceDemand(models.Model):

    _name = "insurance.security.demand"
    _description = "Demande de police d'assurance"

    name = fields.Char("Titre de la demande", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Html("Descritption", copy=False, help='Détails de votre demande. Préciser le produit d\'assurance que vous souhaité', readonly=True)
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
    client_name = fields.Char( related='client_id.name', string="Nom du client", required=True, copy=False, readonly=True)
    client_phone = fields.Char( related='client_id.phone', string="Numéro de téléphone", copy=False, readonly=True)
    client_email = fields.Char( related='client_id.email', string="Email", required=True, copy=False, readonly=True)
    
    product_id = fields.Many2one("insurance.security.product", string = "Choix du produit", readonly=True)
    product_name = fields.Char( related='product_id.name', string="Nom du produit", required=True, copy=False, readonly=True)
    product_type = fields.Char( related='product_id.type_ids.name', string="Type d'assurance", required=True, copy=False, readonly=True)
    product_coverage_for = fields.Selection( related='product_id.coverage_type', string="Type de couvrement", required=True, copy=False, readonly=True)
    
    proofs = fields.Many2many(
        'ir.attachment', 
        string='Preuve avec documents', 
        help='Veuillez insérer les document adéquates stipuler pour appuyer votre demande',
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

    @api.model
    def create(self, values):
        rtn = super().create(values)
        if rtn.name == 'New':
            rtn.name = self.env['ir.sequence'].next_by_code('claims.details') or 'New'
        rtn.state = "progress"
        return rtn 