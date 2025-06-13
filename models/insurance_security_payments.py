from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
from ..utils.cryptofpe import Crypto
import logging

_logger = logging.getLogger(__name__)

class InsurancePayment(models.Model):

    _name = "insurance.security.payments"
    _description = "Versement des primes d'assurance des clients"

    name = fields.Char(string='Numéro de versements', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date = fields.Date(string='Date de versement', 
        required=True, 
        default=fields.Datetime.today())

    policy_id = fields.Many2one("insurance.security.policy", string = "Police d'assurance associé", required=True)
    policy_name = fields.Char( related='policy_id.name', string="Nom de la police", required=True, copy=False, readonly=True, compute = '_compute_policy_name' )
    policy_currency_id = fields.Many2one( related='policy_id.currency_id', string="Devise", copy=False, readonly=True)
    policy_prime = fields.Float( related='policy_id.prime', string="Prime de l'assurance", copy=False, readonly=True)
    agent_name = fields.Char( related='policy_id.agent_name', string="Nom du l'agent", copy=False, readonly=True, )
    client_id = fields.Many2one(related='policy_id.client_id', string='Client', readonly=True)
    client_name = fields.Char( related='policy_id.client_name', string="Nom du client", copy=False, readonly=True)
    
    
    # Initialisation de cryptofpe le code source pour le cryptage et le décryptage
    crypto = Crypto()

    _agent_fields = ['agent_name']
    _client_fields = ['client_name']
    _policy_fields = ['policy_name']

    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('payments.details') or 'New'
        return super(InsurancePayment, self).create(vals)
    
    @api.model
    def export_data(self, fields_to_export):
        """
        Surcharge de la méthode d'exportation pour déchiffrer les champs avant l'exportation.
        """
        # Appel de la méthode d'exportation d'origine pour obtenir les données à exporter
        data = super(InsurancePayment, self).export_data(fields_to_export)

        # Récupérer les indices des champs à déchiffrer
        agents_field_indices = [i for i, field in enumerate(fields_to_export) if field in self._agent_fields]
        clients_field_indices = [i for i, field in enumerate(fields_to_export) if field in self._client_fields]
        policy_field_indices = [i for i, field in enumerate(fields_to_export) if field in self._policy_fields]

        records = self.env['insurance.security.payments'].search([])
        clients_keyset_keys = [record.client_id.keyset_key for record in records]
        agents_keyset_keys = [record.agent_id.keyset_key for record in records]
        i = 0

        # Parcourir les enregistrements pour déchiffrer les champs cryptés
        for row in data['datas']:
            json_clients = clients_keyset_keys[i]
            json_agents = agents_keyset_keys[i]
            i += 1
            for index in agents_field_indices:
                if row[index]:
                    row[index] = self._decrypt_value(row[index], json_agents)
            for index in clients_field_indices:
                if row[index]:
                    row[index] = self._decrypt_value(row[index], json_clients)
            for index in policy_field_indices:
                if row[index]:
                    row[index] = self._decrypt_value(row[index], json_clients)
        return data

    def write(self, vals):
        vals = self._encrypt_fields(vals)
        return super(InsurancePayment, self).write(vals)

    def read(self, fields=None, load='_classic_read'):
        records = super(InsurancePayment, self).read(fields, load)
        return self._decrypt_fields(records)
        
    
    @api.onchange('client_id')
    def onClientChange(self):
        self.policy_id = False

    # Définition du domaine pour le champ policy_id
    @api.onchange('client_id')
    def _onchange_client_id(self):
        if self.client_id:
            return {'domain': {'policy_id': [('client_id', '=', self.client_id.id)]}}
        else:
            return {'domain': {'policy_id': []}}

    """ @api.depends('policy_name')
    def _compute_policy_name(self):
        for record in self:
            if record.policy_name:
                print(policy_name, 'policy_name')
                record.policy_name = record._decrypted_value(record.policy_name) 
             """



    def _decrypt_value(self, value):
        """Déchiffre une valeur si elle n'est pas vide."""
        print(value, 'value')
        try:
            return self.crypto.decrypt_data(value) if value else value
        except Exception as e:
            _logger.error(f"Erreur lors du déchiffrement de la valeur: {e}")
            return value

    def _decrypt_fields(self, records):
        """Déchiffre les champs définis dans _encrypted_fields pour chaque enregistrement."""
        for record in records:
            client_id = record.get('client_id')
            if client_id:
                client = self.env['insurance.security.clients'].browse(client_id[0])
                print(client, 'client')
                json = client.keyset_key
                for field in self._client_fields:
                    # Parcours des enregistrements pour déchiffrer les champs
                    if record[field]:
                        record[field] = self._decrypt_value(record[field], json)
                for field in self._policy_fields:
                    # Parcours des enregistrements pour déchiffrer les champs
                    if record[field]:
                        record[field] = self._decrypt_value(record[field], json)
            agent_id = record.get('agent_id')
            if agent_id:
                agent = self.env['insurance.security.agents'].browse(agent_id[0])
                json = agent.keyset_key
                for field in self._agent_fields:
                    # Parcours des enregistrements pour déchiffrer les champs
                    if record[field]:
                        record[field] = self._decrypt_value(record[field], json)
        return records

