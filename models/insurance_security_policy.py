from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class InsurancePolicy(models.Model):
    _name = "insurance.security.policy"
    _description = "Polices d'assurance"

    name = fields.Char(string='Numéro de Police', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    duration = fields.Integer(string='Temps d\'émission de la police (en mois)', copy=False, required=True)
    start_date = fields.Date(string='Date de Début', required=True)
    end_date = fields.Date(string='Date de Fin', required=True)
    commission = fields.Float(string='Commission en pourcentage', copy=False, required=True)
    state = fields.Selection(
        [
            ('progress', 'En cours'), 
            ('confirmed', 'Confirmer'), 
            ('closed', 'Fermer')
        ],
        required=True, 
        default='progress')
    conditions = fields.Html("Conditions et Obligations", required=True)
    
    proofs = fields.Many2many(
        'ir.attachment', 
        string='Règlements de l\'agence', 
        help='Veuillez insérer les règlements de l\'agence ainsi que tous les autres documents conformément à sa police d\'assurance'
    )
   
    product_id = fields.Many2one("insurance.security.product", string="Produit Associé")
    product_name = fields.Char( related='product_id.name', string="Nom du produit", required=True, copy=False, readonly=True)
    product_type = fields.Char( related='product_id.type_ids.name', string="Type d'assurance", required=True, copy=False, readonly=True)
    product_coverage_for = fields.Selection( related='product_id.coverage_type', string="Type de couvrement", required=True, copy=False, readonly=True)
    currency_id = fields.Many2one(related='product_id.currency_id', string="Devise", required=True, copy=False, readonly=True)
    product_prime_price = fields.Float( related='product_id.prime_price', string="Prime d'assurance", required=True, copy=False, readonly=True)
    product_amount_guarantee = fields.Float( related='product_id.amount_guarantee', string="Montant garantie", required=True, copy=False, readonly=True)
   
    agent_id = fields.Many2one("hr.employee", string = "Agents")
    agent_name = fields.Char( related='agent_id.name', string="Nom du l'agent", required=True, copy=False, readonly=True)
    agent_phone = fields.Char( related='agent_id.phone', string="Numéro de téléphone de l'agent", copy=False, readonly=True)
    agent_email = fields.Char( related='agent_id.private_email', string="Email", copy=False, readonly=True)
    
    client_id = fields.Many2one("res.partner", string = "Client ")
    client_name = fields.Char( related='client_id.name', string="Nom du client", required=True, copy=False, readonly=True)
    client_phone = fields.Char( related='client_id.phone', string="Numéro de téléphone du client", copy=False, readonly=True)
    client_email = fields.Char( related='client_id.email', string="Email", copy=False, readonly=True)


    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration < 0:
                raise ValidationError(
                    "Le temps n'est pas négatif")
    
    @api.constrains('commission')
    def _check_commission(self):
        for record in self:
            if record.commission < 0:
                raise ValidationError(
                    "La commission n'est pas négatif")

    @api.constrains('proofs')
    def _check_proofs(self):
        for record in self:
            if not record.proofs:
                # This can happen if you remove the last attachment.
                return
            for proof in record.proofs:
                if not proof.mimetype:
                    # This can happen if the mimetype is not set.
                    continue
                if proof.mimetype not in ('application/pdf'):
                    raise ValidationError(
                        "Les règlements de l'agence doivent être en pdf")

    @api.onchange("duration")
    def _onchange_date(self):
        if self.duration:
            self.start_date = fields.Datetime.today()
            self.end_date = fields.Datetime.today() + relativedelta(months=self.duration)
        else:
            self.start_date = fields.Datetime.today()
            self.end_date = fields.Datetime.today()
    
    def confirm_insurance(self):
        if self.product_amount_guarantee > 0 and self.product_prime_price > 0:
            self.state = 'confirmed'
        else:
            raise UserError(_("La prime et le montant garanti doit être supérieur à zero"))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('policy.details') or 'New'
        return super(InsurancePolicy, self).create(vals)
