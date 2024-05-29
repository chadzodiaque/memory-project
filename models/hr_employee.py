from odoo import fields, models

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    """ Relations de models"""
    policy_ids = fields.One2many("insurance.security.policy", "agent_id", string="Gestion des polices")
