from odoo import fields, models

class ResPartners (models.Model):
    
    _inherit = "res.partner"

    """ Relations de models"""
    claims_ids = fields.One2many("insurance.security.claims", "client_id", string="Mes reclamations")
    demands_ids = fields.One2many("insurance.security.demand", "client_id", string="Mes demmandes d'assurance ")
    policy_ids = fields.One2many("insurance.security.policy", "client_id", string="Mes polices d'assurance ")


