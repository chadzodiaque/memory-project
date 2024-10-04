{
    'name': 'Insurrance Security',
    'installable' : True,
    'application' : True,
    'depends': ['base', 'hr', 'portal', 'muk_web_theme'],
    'data' : [
        #'security/ir.model.access.csv',
        'reports/ir_actions_report.xml',
        'reports/report_policy.xml',
        'security/security_access_details.xml',
        'views/insurance_security_assistance_views.xml',
        'views/insurance_security_cars_views.xml',
        'views/insurance_security_policy_views.xml',
        'views/insurance_security_demand_views.xml',
        'views/insurance_security_claims_views.xml',
        'views/insurance_security_menus.xml',
        'views/insurance_security_payments_views.xml',
        'views/insurance_security_agents_views.xml',
        'views/insurance_security_clients_views.xml',
        'views/insurance_sequence.xml',  
        'views/portal_templates.xml',

    ],
    
}