from odoo import fields, models

class InsuranceType(models.Model):

    _name = "insurance.security.type"
    _description = "Type d'assurance"

    name = fields.Char("Type d'assurance", required=True, copy=False)
    color = fields.Integer("Color Index")
    coverage_risks = fields.Char("Risques couverts", required=True, copy=False)
    conditions = fields.Html("Conditions de couverture", copy=False, required=True)
    creation_date = fields.Date("Date de creation", default=fields.Datetime.today(), required=True, copy=False, readonly=True)