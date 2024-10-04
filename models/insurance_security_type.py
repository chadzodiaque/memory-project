from odoo import fields, models, api, _
from ..utils.cryptofpe import Crypto
import logging

_logger = logging.getLogger(__name__)

class InsuranceType(models.Model):

    _name = "insurance.security.type"
    _description = "Type d'assurance"

    name = fields.Char("Type d'assurance", required=True, copy=False)
    color = fields.Integer("Color Index")
    coverage_risks = fields.Char("Risques couverts", required=True, copy=False)
    conditions = fields.Html("Conditions de couverture", copy=False, required=True)
    creation_date = fields.Date("Date de creation", default=fields.Datetime.today(), required=True, copy=False, readonly=True)

    # Initialisation de cryptofpe
    crypto = Crypto()

    _encrypted_fields = ['name', 'coverage_risks']

    def _encrypt_value(self, value):
        """Chiffre une valeur si elle n'est pas vide."""
        try:
            if value:
                value_encrypted = self.crypto.encrypt_data(value)
                value_encoded = value_encrypted.encode('utf-8')
                return value_encoded
            else:
                return value
        except Exception as e:
            _logger.error(f"Erreur lors du chiffrement de la valeur: {e}")
            return value

    def _decrypt_value(self, value):
        """Déchiffre une valeur si elle n'est pas vide."""
        try:
            return self.crypto.decrypt_data(value) if value else value
        except Exception as e:
            _logger.error(f"Erreur lors du déchiffrement de la valeur: {e}")
            return value

    def _encrypt_fields(self, vals):
        """Chiffre les champs définis dans _encrypted_fields."""
        for field in self._encrypted_fields:
            print(field,'field')
            if field in vals and vals[field]:
                print(vals[field],'vals[field]')
                vals[field] = self._encrypt_value(vals[field])
        return vals

    def _decrypt_fields(self, records):
        """Déchiffre les champs définis dans _encrypted_fields pour chaque enregistrement."""
        for record in records:
            print(record, 'record')
            for field in self._encrypted_fields:
                if record[field]:
                    #print(record[field],'record[field]')
                    record[field] = self._decrypt_value(record[field])
        return records

    @api.model
    def create(self, vals):
        print(vals,'vals')
        vals = self._encrypt_fields(vals)
        return super(InsuranceType, self).create(vals)

    def write(self, vals):
        vals = self._encrypt_fields(vals)
        return super(InsuranceType, self).write(vals)

    def read(self, fields=None, load='_classic_read'):
        records = super(InsuranceType, self).read(fields, load)
        return self._decrypt_fields(records)
        

    
    # Suppression de la décryption dans fields_view_get, ce n'est pas approprié ici
