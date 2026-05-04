# drug_config.py
# Central configuration for all drugs in the Pharmacogenomic Equity Atlas
# Add new drugs here and they will automatically appear in all scripts

DRUG_DATABASE = {
    'Warfarin': {
        'gene': 'CYP2C9',
        'low_risk': 'Standard dosing (5mg daily)',
        'moderate_risk': 'Consider reduced initial dose (3-4mg)',
        'high_risk': 'Genotype-guided dosing recommended',
        'very_high_risk': 'Alternative anticoagulant (apixaban, rivaroxaban)',
        'gxe_params': {
            'base_risk': 0.05,
            'genetic_effect': 0.15,
            'ses_effect': 0.20,
            'gxe_effect': 0.25
        }
    },
    'Clopidogrel': {
        'gene': 'CYP2C19',
        'low_risk': 'Standard therapy (75mg daily)',
        'moderate_risk': 'Monitor platelet function, consider dose adjustment',
        'high_risk': 'Consider alternative antiplatelet (ticagrelor, prasugrel)',
        'very_high_risk': 'Avoid clopidogrel, use ticagrelor 90mg twice daily',
        'gxe_params': {
            'base_risk': 0.08,
            'genetic_effect': 0.20,
            'ses_effect': 0.15,
            'gxe_effect': 0.30
        }
    },
    'Simvastatin': {
        'gene': 'SLCO1B1',
        'low_risk': 'Standard 40mg daily',
        'moderate_risk': 'Start with 20mg, monitor CK levels',
        'high_risk': 'Use pravastatin or rosuvastatin 10mg',
        'very_high_risk': 'Avoid simvastatin, use alternative statin',
        'gxe_params': {
            'base_risk': 0.03,
            'genetic_effect': 0.25,
            'ses_effect': 0.10,
            'gxe_effect': 0.20
        }
    },
    'Fluorouracil': {
        'gene': 'DPYD',
        'low_risk': 'Standard dosing (500mg/m²)',
        'moderate_risk': 'Consider 25% dose reduction',
        'high_risk': 'Consider 50% dose reduction with monitoring',
        'very_high_risk': 'Avoid fluorouracil, consider alternative',
        'gxe_params': {
            'base_risk': 0.12,
            'genetic_effect': 0.35,
            'ses_effect': 0.25,
            'gxe_effect': 0.40
        }
    },
    'Codeine': {
        'gene': 'CYP2D6',
        'low_risk': 'Standard dosing (30-60mg every 4-6 hours)',
        'moderate_risk': 'Consider 25% dose reduction, monitor for toxicity',
        'high_risk': 'Avoid codeine, consider tramadol or morphine',
        'very_high_risk': 'Avoid completely, use non-opioid alternatives',
        'gxe_params': {
            'base_risk': 0.10,
            'genetic_effect': 0.30,
            'ses_effect': 0.18,
            'gxe_effect': 0.35
        }
    },
    'Tamoxifen': {
        'gene': 'CYP2D6',
        'low_risk': 'Standard dosing (20mg daily for 5 years)',
        'moderate_risk': 'Monitor for reduced efficacy, consider extended duration',
        'high_risk': 'Consider aromatase inhibitor (anastrozole, letrozole)',
        'very_high_risk': 'Switch to anastrozole or letrozole',
        'gxe_params': {
            'base_risk': 0.06,
            'genetic_effect': 0.22,
            'ses_effect': 0.12,
            'gxe_effect': 0.28
        }
    },
    'Phenytoin': {
        'gene': 'CYP2C9',
        'low_risk': 'Standard dosing (300-400mg daily)',
        'moderate_risk': 'Monitor levels more frequently (every 2-4 weeks)',
        'high_risk': 'Consider 25% dose reduction, monitor closely',
        'very_high_risk': 'Consider fosphenytoin or alternative AED',
        'gxe_params': {
            'base_risk': 0.09,
            'genetic_effect': 0.18,
            'ses_effect': 0.22,
            'gxe_effect': 0.32
        }
    },
    'Atorvastatin': {
        'gene': 'SLCO1B1',
        'low_risk': 'Standard dosing (10-20mg daily)',
        'moderate_risk': 'Start with 10mg, monitor CK at 4-6 weeks',
        'high_risk': 'Use pravastatin 20mg or rosuvastatin 5mg',
        'very_high_risk': 'Avoid atorvastatin, use alternative statin',
        'gxe_params': {
            'base_risk': 0.02,
            'genetic_effect': 0.20,
            'ses_effect': 0.08,
            'gxe_effect': 0.18
        }
    },
    'Capecitabine': {
        'gene': 'DPYD',
        'low_risk': 'Standard dosing (1250mg/m² twice daily)',
        'moderate_risk': 'Consider 25% dose reduction with monitoring',
        'high_risk': 'Consider 50% dose reduction, monitor for toxicity',
        'very_high_risk': 'Avoid capecitabine, consider alternative chemotherapy',
        'gxe_params': {
            'base_risk': 0.15,
            'genetic_effect': 0.40,
            'ses_effect': 0.28,
            'gxe_effect': 0.45
        }
    },
    'Carbamazepine': {
        'gene': 'HLA-B',
        'low_risk': 'Standard dosing',
        'moderate_risk': 'Monitor for rash',
        'high_risk': 'Screen for HLA-B*1502 allele',
        'very_high_risk': 'Avoid carbamazepine, use alternative',
        'gxe_params': {
            'base_risk': 0.01,
            'genetic_effect': 0.50,
            'ses_effect': 0.05,
            'gxe_effect': 0.10
        }
    }
}

def get_drug_list():
    """Return list of all drug names"""
    return list(DRUG_DATABASE.keys())

def get_drug_info(drug_name):
    """Return full drug information"""
    return DRUG_DATABASE.get(drug_name, None)

def get_drug_gene(drug_name):
    """Return the gene associated with a drug"""
    info = DRUG_DATABASE.get(drug_name, {})
    return info.get('gene', 'Unknown')

def get_drug_recommendation(drug_name, risk_category):
    """Get recommendation for a specific drug and risk category"""
    info = DRUG_DATABASE.get(drug_name, {})
    risk_key = risk_category.lower().replace(' ', '_')
    mapping = {
        'low_risk': 'low_risk',
        'moderate_risk': 'moderate_risk', 
        'high_risk': 'high_risk',
        'very_high_risk': 'very_high_risk'
    }
    return info.get(mapping.get(risk_key, 'low_risk'), 'Consult clinical pharmacist')

def get_gxe_params(drug_name):
    """Get GxE parameters for a drug"""
    info = DRUG_DATABASE.get(drug_name, {})
    return info.get('gxe_params', {
        'base_risk': 0.05,
        'genetic_effect': 0.15,
        'ses_effect': 0.10,
        'gxe_effect': 0.20
    })

# Drug classes for organization
DRUG_CLASSES = {
    'Anticoagulants': ['Warfarin'],
    'Antiplatelets': ['Clopidogrel'],
    'Statins': ['Simvastatin', 'Atorvastatin'],
    'Chemotherapy': ['Fluorouracil', 'Capecitabine'],
    'Opioids': ['Codeine'],
    'Hormonal Therapy': ['Tamoxifen'],
    'Antiepileptics': ['Phenytoin', 'Carbamazepine']
}

def get_drug_class(drug_name):
    """Return the class of a drug"""
    for drug_class, drugs in DRUG_CLASSES.items():
        if drug_name in drugs:
            return drug_class
    return 'Other'
