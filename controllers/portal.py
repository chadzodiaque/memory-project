from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from ..utils.cryptofpe import Crypto
from odoo import http, _
import re
import logging

_logger = logging.getLogger(__name__)




class InsurancePortalAccount(CustomerPortal):

    crypto = Crypto()
    
    def _decrypt_value(self, value):
        """Déchiffre une valeur si elle n'est pas vide."""
        print(value, 'valueT')
        try:
            return self.crypto.decrypt_data(value) 
        except Exception as e:
            _logger.error(f"Erreur lors du déchiffrement de la valeur: {e}")
            return value
   
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'insurance_count' in counters:

            insurance_policy_count = request.env['insurance.security.policy'].search_count([
                ('client_id', '=', request.env.user.partner_id.id),
                ('state', '=', 'confirmed')
            ]) if request.env['insurance.security.policy'].check_access_rights('read', raise_exception=False) else 0
            
            insurance_demand_count = request.env['insurance.security.demand'].search_count([
                ('client_id', '=', request.env.user.partner_id.id)
            ]) if request.env['insurance.security.demand'].check_access_rights('read', raise_exception=False) else 0
            
            insurance_claims_count = request.env['insurance.security.claims'].search_count([
                ('client_id', '=', request.env.user.partner_id.id)
            ]) if request.env['insurance.security.claims'].check_access_rights('read', raise_exception=False) else 0
            
            insurance_payments_count = request.env['insurance.security.payments'].search_count([
                ('client_id', '=', request.env.user.partner_id.id)
            ]) if request.env['insurance.security.payments'].check_access_rights('read', raise_exception=False) else 0
            
            insurance_assistance_count = request.env['insurance.security.assistance'].search_count([
                ('user_id', '=', request.env.user.partner_id.id)
            ]) if request.env['insurance.security.assistance'].check_access_rights('read', raise_exception=False) else 0
            
            insurance_count = insurance_policy_count + insurance_demand_count + insurance_claims_count + insurance_payments_count + insurance_assistance_count
            
            values['insurance_count'] = str(insurance_count) if insurance_count == 0 else insurance_count
        return values
    
    @http.route(['/my/insurance'], type='http', website=True)
    def myInsuranceview(self, **kw):
        
        policies = request.env['insurance.security.policy'].search([
            ('state', '=', 'confirmed')
        ])

        insurance_policy_count = insurance_policy_count = request.env['insurance.security.policy'].search_count([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id)
        ])

        insurance_demand_count = request.env['insurance.security.demand'].search_count([
            ('client_id', '=', request.env.user.partner_id.id)
        ])
        
        
        insurance_claims_count = request.env['insurance.security.claims'].search_count([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id)
        ])

        insurance_payments_count = request.env['insurance.security.payments'].search_count([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id)
        ])

        insurance_assistance_count = request.env['insurance.security.assistance'].search_count([
            ('user_id', '=', request.env.user.partner_id.id)
        ])
        
        values = {
            'insurance_policy_count': insurance_policy_count, 
            'page_name': 'portal_my_insurance', 
            'insurance_demand_count': insurance_demand_count, 
            'insurance_claims_count': insurance_claims_count,
            'insurance_payments_count': insurance_payments_count,
            'insurance_assistance_count': insurance_assistance_count
            }
        return request.render("insurance_security.portal_my_insurance", values)

    @http.route(['/my/insurance/assistances', '/my/insurance/assistances/page/<int:page>'], type='http', website=True)
    def insuranceportalAssistanceview(self, page=1, sortby=None, **kw):
        
        
        sorted_list = {
            'id': {'label' : _('ID'), 'order': 'id'},
            'name': {'label' : _('Intitulé de l\'assistance'), 'order': 'name'},
        }

        if not sortby:
            sortby = 'id'

        default_order_by = sorted_list[sortby]['order']
        total_assistance = request.env['insurance.security.assistance'].search_count([
            ('user_id', '=', request.env.user.partner_id.id)
        ])

        page_detail = pager(url='/my/insurance/assistances',
                            total=total_assistance,
                            page=page,
                            url_args={'sortby':sortby},
                            step=10)

        my_assistance = request.env['insurance.security.assistance'].sudo().search([
            ('user_id', '=', request.env.user.partner_id.id)
            ],
            limit=10,
            order=default_order_by,
            offset=page_detail['offset'])

        values = {
            'assistances': my_assistance, 
            'page_name': 'portal_list_assistances', 
            'pager': page_detail, 
            'searchbar_sortings': sorted_list,
            'sortby': sortby
            }
        return request.render("insurance_security.portal_list_assistances", values)

    @http.route(['/my/insurance/assistances/<model("insurance.security.assistance"):assistance_id>'], type='http', website=True)
    def insuranceportalAssitanceFormview(self, assistance_id,  **kw):
        values = {'assistance': assistance_id, 'page_name': 'portal_assistances_form_view'}
        my_assistance = request.env['insurance.security.assistance'].sudo().search([
            ('user_id', '=', request.env.user.partner_id.id),
            ])
        assistance_ids = my_assistance.ids
        assistance_index = assistance_ids.index(assistance_id.id)
        if assistance_index != 0 and assistance_ids[assistance_index - 1]:
            values['prev_record'] = '/my/insurance/assistances/{}'.format(assistance_ids[assistance_index-1])
        if assistance_index < len(assistance_ids) - 1 and assistance_ids[assistance_index+1]:
            values['next_record'] = '/my/insurance/assistances/{}'.format(assistance_ids[assistance_index+1])        

        return request.render("insurance_security.portal_assistance_form_view", values)

    @http.route(['/my/insurance/policies', '/my/insurance/policies/page/<int:page>'], type='http', website=True)
    def insuranceportalPolicyview(self, page=1, sortby=None, **kw):  
        _encrypted_fields = ['name', 'duration',  'prime', 'agent_name', 'agent_phone', 'agent_email', 'client_name', 'client_phone', 'client_email']

        sorted_list = {
            'id': {'label' : _('ID'), 'order': 'id'},
            'name': {'label' : _('Numero de police'), 'order': 'name'},
        }

        if not sortby:
            sortby = 'id'

        default_order_by = sorted_list[sortby]['order']
        total_policy = request.env['insurance.security.policy'].search_count([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ('state', '=', 'confirmed'),
            
        ])

        page_detail = pager(url='/my/insurance/policies',
                            total=total_policy,
                            page=page,
                            url_args={'sortby':sortby},
                            step=10)

        my_policy = request.env['insurance.security.policy'].sudo().search([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ('state', '=', 'confirmed'),
            ],
            limit=10,
            order=default_order_by,
            offset=page_detail['offset'])

        values = {
            'policies': policies, 
            'page_name': 'portal_list_policies', 
            'pager': page_detail, 
            'searchbar_sortings': sorted_list,
            'sortby': sortby
            }
        return request.render("insurance_security.portal_list_policies", values)

    @http.route(['/my/insurance/policies/<model("insurance.security.policy"):policy_id>'], type='http', website=True)
    def insuranceportalPolicyFormview(self, policy_id,  **kw):
        values = {'policy': policy_id, 'page_name': 'portal_policies_form_view'}
        my_policy = request.env['insurance.security.policy'].sudo().search([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ('state', '=', 'confirmed'),
            ])

        policy_ids = my_policy.ids
        policy_index = policy_ids.index(policy_id.id)
        if policy_index != 0 and policy_ids[policy_index - 1]:
            values['prev_record'] = '/my/insurance/policies/{}'.format(policy_ids[policy_index-1])
        if policy_index < len(policy_ids) - 1 and policy_ids[policy_index+1]:
            values['next_record'] = '/my/insurance/policies/{}'.format(policy_ids[policy_index+1])        

        return request.render("insurance_security.portal_policy_form_view", values)

    @http.route(['/my/insurance/demands', '/my/insurance/demands/page/<int:page>'], type='http', website=True)
    def insuranceportalDemandview(self, page=1, sortby=None, **kw):

        
        sorted_list = {
            'id': {'label' : _('ID'), 'order': 'id desc'},
            'name': {'label' : _('Name'), 'order': 'name'},
        }

        if not sortby:
            sortby = 'id'

        default_order_by = sorted_list[sortby]['order']
        total_demands = request.env['insurance.security.demand'].search_count([
            ('client_id', '=', request.env.user.partner_id.id),
            
        ])

        page_detail = pager(url='/my/insurance/demands',
                            total=total_demands,
                            page=page,
                            url_args={'sortby':sortby},
                            step=10)

        my_demands = request.env['insurance.security.demand'].search([
            ('client_id', '=', request.env.user.partner_id.id),
            ],
            limit=10,
            order=default_order_by,
            offset=page_detail['offset'])

        values = {
            'demands': my_demands, 
            'page_name': 'portal_list_demands', 
            'pager': page_detail, 
            'searchbar_sortings': sorted_list,
            'sortby': sortby
            }
        return request.render("insurance_security.portal_list_demands", values)

    @http.route(['/my/insurance/demands/<model("insurance.security.demand"):demand_id>'], type='http', website=True)
    def insuranceportalDemandFormview(self, demand_id,  **kw):
        values = {'demand': demand_id, 'page_name': 'portal_demands_form_view'}
        my_demand = request.env['insurance.security.demand'].search([
            ('client_id', '=', request.env.user.partner_id.id),
            ])
        demand_ids = my_demand.ids
        demand_index = demand_ids.index(demand_id.id)
        if demand_index != 0 and demand_ids[demand_index - 1]:
            values['prev_record'] = '/my/insurance/demands/{}'.format(demand_ids[demand_index-1])
        if demand_index < len(demand_ids) - 1 and demand_ids[demand_index+1]:
            values['next_record'] = '/my/insurance/demands/{}'.format(demand_ids[demand_index+1])        

        return request.render("insurance_security.portal_demand_form_view", values)


    @http.route(['/my/insurance/claims', '/my/insurance/claims/page/<int:page>'], type='http', website=True)
    def insuranceportalClaimview(self, page=1, sortby=None, **kw):
        
        
        sorted_list = {
            'id': {'label' : _('ID'), 'order': 'id desc'},
            'name': {'label' : _('Numéro'), 'order': 'name'},
        }

        if not sortby:
            sortby = 'id'

        default_order_by = sorted_list[sortby]['order']
        total_claims = request.env['insurance.security.claims'].search_count([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            
        ])

        page_detail = pager(url='/my/insurance/claims',
                            total=total_claims,
                            page=page,
                            url_args={'sortby':sortby},
                            step=10)

        my_claims = request.env['insurance.security.claims'].search([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ],
            limit=10,
            order=default_order_by,
            offset=page_detail['offset'])

        values = {
            'claims': my_claims, 
            'page_name': 'portal_list_claims', 
            'pager': page_detail, 
            'searchbar_sortings': sorted_list,
            'sortby': sortby
            }
        return request.render("insurance_security.portal_list_claims", values)

    @http.route(['/my/insurance/claims/<model("insurance.security.claims"):claim_id>'], type='http', website=True)
    def insuranceportalClaimFormview(self, claim_id,  **kw):
        values = {'claim': claim_id, 'page_name': 'portal_claims_form_view'}
        my_claim = request.env['insurance.security.claims'].search([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ])
        claim_ids = my_claim.ids
        claim_index = claim_ids.index(claim_id.id)
        if claim_index != 0 and claim_ids[claim_index - 1]:
            values['prev_record'] = '/my/insurance/claims/{}'.format(claim_ids[claim_index-1])
        if claim_index < len(claim_ids) - 1 and claim_ids[claim_index+1]:
            values['next_record'] = '/my/insurance/claims/{}'.format(claim_ids[claim_index+1])        

        return request.render("insurance_security.portal_claim_form_view", values)

    """ form new assistance """
    @http.route(['/my/insurance/assistances/new'], type='http', methods=["POST", "GET"], website=True)
    def registerAssistanceinsurance(self, **kw):
        values = {
            'page_name': 'portal_new_demand_assistance', 
        }
        
        if request.httprequest.method == "POST":
            error_list = []
            if not kw.get("name"):
                error_list.append("Name field is mandatory. ")
            if not kw.get("email"):
                error_list.append("Email field is mandatory. ")

            if not kw.get("description"):
                error_list.append("Description field is mandatory. ")
            client_id = request.env.user.partner_id.id
            
            if not error_list:
                client_id = request.env.user.partner_id.id
                if not client_id:
                    
                    request.env['insurance.security.assistance'].create({
                        "name": kw.get("name"),
                        "email": kw.get("email"),
                        "description": kw.get("description"),
                    })
                    
                    success = "Demande d'assistance envoyée avec succes !"
                    values['success_msg'] = success
                    return request.redirect('/my/insurance/demands?message=' + success)
                else:
                    request.env['insurance.security.assistance'].create({
                        "name": kw.get("name"),
                        "email": kw.get("email"),
                        "user_id": client_id,
                        "description": kw.get("description")
                    })
                    
                    success = "Demande d'assistance envoyée avec succes !"
                    values['success_msg'] = success
                    return request.redirect('/my/insurance/assistances?message=' + success)
                
            else:
                values['error_list'] = error_list
            
        return request.render("insurance_security.portal_new_demand_assistance", values)

    """ form new demand """
    @http.route(['/my/insurance/demands/new'], type='http', methods=["POST", "GET"], website=True)
    def registerDemandinsurance(self, **kw):
    
        values = {
            'page_name': 'portal_new_demand_insurance', 
        }
        
        if request.httprequest.method == "POST":
            error_list = []
            if not kw.get("name"):
                error_list.append("Specify the title ")

            if not kw.get("cars_number"):
                error_list.append("Number of cars is mandatory. ")

            if not kw.get("description"):
                error_list.append("You should specify your motivation ")
            
            if not kw.get("proofs"):
                error_list.append("Proofs field is mandatory. ")
            if not error_list:
                attachment_ids = []
                for file in request.httprequest.files.getlist('proofs'):
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'type': 'binary',
                        'datas': file.read(),
                        'res_model': 'insurance.security.demand',
                    })
                    attachment_ids.append(attachment.id)
                request.env['insurance.security.demand'].sudo().create({
                    "name": kw.get("name"),
                    "client_id": request.env.user.partner_id.id,
                    "description": kw.get("description"),
                    "cars_number": kw.get("cars_number"),
                    "proofs" : [(6, 0,attachment_ids )]    
                })
                
                success = "Demande de police d'assurance auto envoyée avec succès!"
                return request.redirect('/my/insurance/demands?message=' + success)
                
            else:
                values['error_list'] = error_list
            
        return request.render("insurance_security.portal_new_demand_insurance", values)

    """ form new claim """
    @http.route(['/my/insurance/claims/new/claim'], type='http', methods=["POST", "GET"], website=True)
    def registerClaiminsurance(self, **kw):
        policies = request.env['insurance.security.policy'].search([
            ('client_id', '=', request.env.user.partner_id.id),
        ])
        values = {
            'page_name': 'portal_new_claim_insurance', 
            'policies': policies,
        }
        
        if request.httprequest.method == "POST":
            error_list = []
            
            if not kw.get("description"):
                error_list.append("Description field is mandatory. ")
            if not kw.get("policy"):
                error_list.append("Policy field is mandatory. ")
            if not kw.get("policy").isdigit():
                error_list.append("Invalid Policy field. ")
            
            if not kw.get("proofs"):
                error_list.append("Document field is mandatory. ")
            if not error_list:
                attachment_ids = []
                for file in request.httprequest.files.getlist('proofs'):
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'type': 'binary',
                        'datas': file.read(),
                        'res_model': 'insurance.security.demand',
                        'res_id' : int(kw.get("policy"))
                    })
                    attachment_ids.append(attachment.id)
                request.env['insurance.security.claims'].sudo().create({
                    "description": kw.get("description"),
                    "policy_id": int(kw.get("policy")),
                    "proofs" : [(6, 0,attachment_ids )]    
                })
                success = "Successfully claim registered!"
                values['success_msg'] = success
                return request.redirect('/my/insurance/claims?message=' + success)
            else:
                values['error_list'] = error_list
           
        return request.render("insurance_security.portal_new_claim_insurance", values)

    @http.route(['/my/insurance/payments', '/my/insurance/payments/page/<int:page>'], type='http', website=True)
    def insuranceportalPaymentview(self, page=1, sortby=None, **kw):
        
        sorted_list = {
            'id': {'label' : _('ID'), 'order': 'id desc'},
            'name': {'label' : _('Numéro de payment'), 'order': 'name'},
        }

        if not sortby:
            sortby = 'id'

        default_order_by = sorted_list[sortby]['order']
        total_payments = request.env['insurance.security.payments'].search_count([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            
        ])

        page_detail = pager(url='/my/insurance/payments',
                            total=total_payments,
                            page=page,
                            url_args={'sortby':sortby},
                            step=10)

        my_payments = request.env['insurance.security.payments'].search([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ],
            limit=10,
            order=default_order_by,
            offset=page_detail['offset'])

        values = {
            'payments': my_payments, 
            'page_name': 'portal_list_payments', 
            'pager': page_detail, 
            'searchbar_sortings': sorted_list,
            'sortby': sortby
            }
        return request.render("insurance_security.portal_list_payments", values)

    @http.route(['/my/insurance/payments/<model("insurance.security.payments"):payment_id>'], type='http', website=True)
    def insuranceportalPaymentFormview(self, payment_id,  **kw):
        values = {
            'payment': payment_id, 
            'page_name': 'portal_payments_form_view'}
        my_payment= request.env['insurance.security.payments'].search([
            ('client_id.related_partner.id', '=', request.env.user.partner_id.id),
            ])
        payment_ids = my_payment.ids
        payment_index = payment_ids.index(payment_id.id)
        if payment_index != 0 and payment_ids[payment_index - 1]:
            values['prev_record'] = '/my/insurance/payments/{}'.format(payment_ids[payment_index-1])
        if payment_index < len(payment_ids) - 1 and payment_ids[payment_index+1]:
            values['next_record'] = '/my/insurance/payments/{}'.format(payment_ids[payment_index+1])        

        return request.render("insurance_security.portal_payment_form_view", values)

    