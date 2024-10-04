from odoo import fields, models

class ResPartners (models.Model):
    
    _inherit = "res.partner"

    cars_number = fields.Integer(string="Nombre de véhicules", readonly=True, copy=False)
    proofs = fields.Many2many(
        'ir.attachment', 
        string='Preuves ', 
        help=' Insérer les documents suivants : Carte d\'identité ou passport, Carte grise(s), Permis de conduire, TVM et Attestion de controle technique',
        readonly=True
    )
    
    """ Relations de models"""
    claims_ids = fields.One2many("insurance.security.claims", "client_id", string="Mes reclamations")
    demands_ids = fields.One2many("insurance.security.demand", "client_id", string="Mes demmandes d'assurance ")
    policy_ids = fields.One2many("insurance.security.policy", "client_id", string="Mes polices d'assurance ")


