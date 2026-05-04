# 07_gxe_modeling_multi_drug.py
# Step 4 - Multi-Drug GxE Interaction Modeling

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 4: Multi-Drug GxE Interaction Modeling")
print("="*60)

# Define drug-specific parameters
DRUG_PARAMETERS = {
    'Warfarin': {
        'gene': 'CYP2C9',
        'base_risk': 0.05,
        'genetic_effect': 0.15,
        'ses_effect': 0.20,
        'gxe_effect': 0.25,
        'clinical_action': 'Dose adjustment needed'
    },
    'Clopidogrel': {
        'gene': 'CYP2C19',
        'base_risk': 0.08,
        'genetic_effect': 0.20,
        'ses_effect': 0.15,
        'gxe_effect': 0.30,
        'clinical_action': 'Alternative therapy recommended'
    },
    'Simvastatin': {
        'gene': 'SLCO1B1',
        'base_risk': 0.03,
        'genetic_effect': 0.25,
        'ses_effect': 0.10,
        'gxe_effect': 0.20,
        'clinical_action': 'Consider alternative statin'
    },
    'Fluorouracil': {
        'gene': 'DPYD',
        'base_risk': 0.12,
        'genetic_effect': 0.35,
        'ses_effect': 0.25,
        'gxe_effect': 0.40,
        'clinical_action': 'Dose reduction required'
    },
    'Codeine': {
        'gene': 'CYP2D6',
        'base_risk': 0.10,
        'genetic_effect': 0.30,
        'ses_effect': 0.18,
        'gxe_effect': 0.35,
        'clinical_action': 'Avoid in poor metabolizers'
    },
    'Tamoxifen': {
        'gene': 'CYP2D6',
        'base_risk': 0.06,
        'genetic_effect': 0.22,
        'ses_effect': 0.12,
        'gxe_effect': 0.28,
        'clinical_action': 'Consider aromatase inhibitor'
    },
    'Phenytoin': {
        'gene': 'CYP2C9',
        'base_risk': 0.09,
        'genetic_effect': 0.18,
        'ses_effect': 0.22,
        'gxe_effect': 0.32,
        'clinical_action': 'Monitor levels closely'
    },
    'Atorvastatin': {
        'gene': 'SLCO1B1',
        'base_risk': 0.02,
        'genetic_effect': 0.20,
        'ses_effect': 0.08,
        'gxe_effect': 0.18,
        'clinical_action': 'Use pravastatin instead'
    },
    'Capecitabine': {
        'gene': 'DPYD',
        'base_risk': 0.15,
        'genetic_effect': 0.40,
        'ses_effect': 0.28,
        'gxe_effect': 0.45,
        'clinical_action': 'Significant dose reduction'
    }
}

print(f"\n[1/6] Analyzing {len(DRUG_PARAMETERS)} drugs for GxE interactions...")

# Store results for all drugs
all_results = []

for drug_name, params in DRUG_PARAMETERS.items():
    print(f"\n  Analyzing {drug_name} ({params['gene']})...")
    
    # Generate data for this drug
    np.random.seed(42)
    n_enhanced = 5000
    
    genotypes = np.random.choice([0, 1, 2], n_enhanced, p=[0.6, 0.35, 0.05])
    ses_scores = np.random.beta(2, 2, n_enhanced)
    
    # Calculate risk with drug-specific parameters
    risks = (params['base_risk'] + 
             genotypes * params['genetic_effect'] +
             ses_scores * params['ses_effect'] +
             genotypes * ses_scores * params['gxe_effect'])
    risks = np.clip(risks, 0.01, 0.50)
    
    toxicities = np.random.binomial(1, risks)
    
    # Create dataframe
    drug_df = pd.DataFrame({
        'genotype': genotypes,
        'ses_score': ses_scores,
        'toxicity': toxicities
    })
    
    # Fit models
    model_main = logit("toxicity ~ genotype + ses_score", data=drug_df).fit(disp=0)
    model_interaction = logit("toxicity ~ genotype * ses_score", data=drug_df).fit(disp=0)
    
    # Store results
    all_results.append({
        'drug': drug_name,
        'gene': params['gene'],
        'main_genotype_effect': model_main.params['genotype'],
        'main_genotype_p': model_main.pvalues['genotype'],
        'gxe_interaction': model_interaction.params['genotype:ses_score'],
        'gxe_pvalue': model_interaction.pvalues['genotype:ses_score'],
        'significant_gxe': model_interaction.pvalues['genotype:ses_score'] < 0.05,
        'clinical_action': params['clinical_action']
    })

# Create results dataframe
results_df = pd.DataFrame(all_results)
results_df = results_df.sort_values('gxe_pvalue')

print("\n" + "="*60)
print("GxE INTERACTION RESULTS BY DRUG")
print("="*60)
print(results_df[['drug', 'gene', 'gxe_interaction', 'gxe_pvalue', 'significant_gxe', 'clinical_action']].to_string(index=False))

# Identify drugs with significant GxE
significant_drugs = results_df[results_df['significant_gxe']]
print(f"\n✓ Drugs with SIGNIFICANT GxE interaction: {len(significant_drugs)}")
if len(significant_drugs) > 0:
    for _, row in significant_drugs.iterrows():
        print(f"   • {row['drug']}: p={row['gxe_pvalue']:.4f}")

# Create visualization
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
axes = axes.flatten()

for idx, drug_name in enumerate(DRUG_PARAMETERS.keys()):
    if idx >= 9:
        break
    
    # Get drug parameters
    params = DRUG_PARAMETERS[drug_name]
    
    # Generate data for plotting
    ses_grid = np.linspace(0, 1, 50)
    
    for genotype in [0, 1, 2]:
        log_odds = (params['base_risk'] + 
                   genotype * params['genetic_effect'] +
                   ses_grid * params['ses_effect'] +
                   genotype * ses_grid * params['gxe_effect'])
        probs = 1 / (1 + np.exp(-log_odds))
        axes[idx].plot(ses_grid, probs, 
                      label=f'{genotype} alt alleles', 
                      linewidth=2)
    
    axes[idx].set_title(f'{drug_name} ({params["gene"]})')
    axes[idx].set_xlabel('SES Score')
    axes[idx].set_ylabel('Toxicity Probability')
    axes[idx].legend(fontsize=8)
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/multi_drug_gxe_plot.png', dpi=150)
print("\n  ✓ Saved: data/processed/multi_drug_gxe_plot.png")

# Save results
results_df.to_csv("data/processed/multi_drug_gxe_results.csv", index=False)
print("  ✓ Saved: data/processed/multi_drug_gxe_results.csv")

print("\n" + "="*60)
print("✓ MULTI-DRUG GXE ANALYSIS COMPLETE!")
print("="*60)
