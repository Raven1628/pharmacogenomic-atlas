# 07_gxe_modeling_multi_drug.py
# Step 4 - Multi-Drug GxE Interaction Modeling (Uses central drug config)

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from scipy import stats
import matplotlib.pyplot as plt
from drug_config import DRUG_DATABASE, get_drug_list, get_gxe_params
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 4: Multi-Drug GxE Interaction Modeling")
print("="*60)

# Get drugs from central config
drugs_to_analyze = get_drug_list()
print(f"\n[1/5] Analyzing {len(drugs_to_analyze)} drugs from central config...")

# Store results for all drugs
all_results = []

for drug_name in drugs_to_analyze:
    params = get_gxe_params(drug_name)
    gene = DRUG_DATABASE[drug_name]['gene']
    
    print(f"\n  Analyzing {drug_name} ({gene})...")
    
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
        'gene': gene,
        'main_genotype_effect': model_main.params['genotype'],
        'main_genotype_p': model_main.pvalues['genotype'],
        'gxe_interaction': model_interaction.params['genotype:ses_score'],
        'gxe_pvalue': model_interaction.pvalues['genotype:ses_score'],
        'significant_gxe': model_interaction.pvalues['genotype:ses_score'] < 0.05,
        'clinical_action': DRUG_DATABASE[drug_name].get('high_risk', 'Monitor closely')[:50]
    })

# Create results dataframe
results_df = pd.DataFrame(all_results)
results_df = results_df.sort_values('gxe_pvalue')

print("\n" + "="*60)
print("GxE INTERACTION RESULTS BY DRUG")
print("="*60)
print(results_df[['drug', 'gene', 'gxe_interaction', 'gxe_pvalue', 'significant_gxe']].to_string(index=False))

# Identify drugs with significant GxE
significant_drugs = results_df[results_df['significant_gxe']]
print(f"\n✓ Drugs with SIGNIFICANT GxE interaction: {len(significant_drugs)}")
if len(significant_drugs) > 0:
    for _, row in significant_drugs.iterrows():
        print(f"   • {row['drug']}: p={row['gxe_pvalue']:.4f}")

# Create visualization (max 9 drugs)
n_plots = min(len(drugs_to_analyze), 9)
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
axes = axes.flatten()

for idx, drug_name in enumerate(drugs_to_analyze[:9]):
    params = get_gxe_params(drug_name)
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
    
    axes[idx].set_title(f'{drug_name} ({DRUG_DATABASE[drug_name]["gene"]})')
    axes[idx].set_xlabel('SES Score')
    axes[idx].set_ylabel('Toxicity Probability')
    axes[idx].legend(fontsize=8)
    axes[idx].grid(True, alpha=0.3)

# Hide unused subplots
for idx in range(len(drugs_to_analyze[:9]), 9):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('data/processed/multi_drug_gxe_plot.png', dpi=150)
print("\n  ✓ Saved: data/processed/multi_drug_gxe_plot.png")

# Save results
results_df.to_csv("data/processed/multi_drug_gxe_results.csv", index=False)
print("  ✓ Saved: data/processed/multi_drug_gxe_results.csv")

print("\n" + "="*60)
print("✓ MULTI-DRUG GXE ANALYSIS COMPLETE!")
print("="*60)
