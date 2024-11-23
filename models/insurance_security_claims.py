from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

from ..utils.cryptofpe import Crypto
import logging

_logger = logging.getLogger(__name__)

class InsuranceClaims(models.Model):
    _name = "insurance.security.claims"
    _description = "Déclaration de sinistres"

    name = fields.Char(string='Numéro de sinistre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    description = fields.Html("Descritption d'un sinistre", copy=False,  help='Détails de sinistre', readonly=True)
    date_claims = fields.Date(
        string='Date de sinistre', 
        required=True,
        readonly=True,
        default=fields.Datetime.today()
    )

    currency_id = fields.Many2one("res.currency", string="Devise")
    compensation= fields.Float("Montant de l'indemnisation ", copy=False, help=' Montant d\'argent que le client a reçu comme indemnisation lors d\'un sinistre. ')

    state = fields.Selection(
        selection=[
            ("progress", "En cours de traitement"),
            ("validated", "Acceptée"),
            ("refused", "Refusée"),
            ("sold", "Soldée")
        ],
        string="Status de l'indemnisation",
        required=True,
        copy=False,
        default="progress",
    )
    proofs = fields.Many2many(
        'ir.attachment', 
        string='Preuve de sinistre en appui', 
        help='Veuillez insérer les preuves de l\'incident ainsi que tous les autres documents pour que votre sinistres soit validée',
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

    agent_name = fields.Char( related='policy_id.agent_name', string="Nom du l'agent", required=True, copy=False, readonly=True)
    agent_phone = fields.Char( related='policy_id.agent_phone', string="Numéro de téléphone", required=True, copy=False, readonly=True)
    agent_email = fields.Char( related='policy_id.agent_email', string="Email", required=True, copy=False, readonly=True)

    # Initialisation de cryptofpe le code source pour le cryptage et le décryptage
    crypto = Crypto()

    _agent_fields = ['agent_name', 'agent_phone', 'agent_email']
    _client_fields = ['client_name', 'client_phone', 'client_email']
    _policy_fields = ['policy_name']

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
                                "price_unit": prop.compensation,
                            },
                        ),
                    ],
                }
            )
        
    def _decrypt_value(self, value, keyset_key):
        """Déchiffre une valeur si elle n'est pas vide."""
        try:
            return self.crypto.decrypt_data(value, keyset_key) if value else value
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


    @api.model
    def create(self, values):
        rtn = super().create(values)
        if rtn.name == 'New':
            rtn.name = self.env['ir.sequence'].next_by_code('claims.details') or 'New'
        rtn.state = "progress"
        return rtn

    def read(self, fields=None, load='_classic_read'):
        records = super(InsuranceClaims, self).read(fields, load)
        return self._decrypt_fields(records)
    
    @api.model
    def export_data(self, fields_to_export):
        """
        Surcharge de la méthode d'exportation pour déchiffrer les champs avant l'exportation.
        """
        # Appel de la méthode d'exportation d'origine pour obtenir les données à exporter
        data = super(InsuranceClaims, self).export_data(fields_to_export)

        # Récupérer les indices des champs à déchiffrer
        agents_field_indices = [i for i, field in enumerate(fields_to_export) if field in self._agent_fields]
        clients_field_indices = [i for i, field in enumerate(fields_to_export) if field in self._client_fields]
        policy_field_indices = [i for i, field in enumerate(fields_to_export) if field in self._policy_fields]

        records = self.env['insurance.security.claims'].search([])
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

    


    