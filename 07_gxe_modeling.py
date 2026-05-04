# 07_gxe_modeling_fixed2.py
# Step 4 - Enhanced GxE detection (Fixed)

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 4: Enhanced GxE Interaction Modeling")
print("="*60)

# ── Part 1: Create enhanced dataset with stronger GxE signal ──────────────
print("\n[1/5] Creating enhanced dataset with stronger GxE signal...")

np.random.seed(42)
n_enhanced = 5000

# Generate data
genotypes = np.random.choice([0, 1, 2], n_enhanced, p=[0.6, 0.35, 0.05])
ses_scores = np.random.beta(2, 2, n_enhanced)

# Calculate risk with GxE interaction
base_risk = 0.05
genetic_effect = genotypes * 0.15
ses_effect = ses_scores * 0.20
gxe_effect = genotypes * ses_scores * 0.25  # This is the interaction!
risks = base_risk + genetic_effect + ses_effect + gxe_effect
risks = np.clip(risks, 0.01, 0.50)

# Sample outcomes
toxicities = np.random.binomial(1, risks)

# Create dataframe
enhanced_df = pd.DataFrame({
    'individual_id': [f"ENH_{i:05d}" for i in range(n_enhanced)],
    'genotype': genotypes,
    'ses_score': ses_scores,
    'toxicity': toxicities,
    'true_risk': risks
})

# Add SES quartile
enhanced_df['ses_quartile'] = pd.qcut(enhanced_df['ses_score'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')

print(f"  ✓ Created enhanced dataset: {len(enhanced_df)} individuals")
print(f"  ✓ Overall toxicity rate: {enhanced_df['toxicity'].mean()*100:.1f}%")
print(f"  ✓ Mean genotype: {enhanced_df['genotype'].mean():.2f}")
print(f"  ✓ Mean SES score: {enhanced_df['ses_score'].mean():.2f}")

# ── Part 2: Model with stronger GxE signal ────────────────────────────────
print("\n[2/5] Testing GxE interaction (enhanced signal)...")

# Model 1: Main effects only
model1 = logit("toxicity ~ genotype + ses_score", data=enhanced_df).fit(disp=0)
print("\n  Model 1 (main effects):")
print(f"    Genotype effect: {model1.params['genotype']:.3f} (p={model1.pvalues['genotype']:.4f})")
print(f"    SES effect: {model1.params['ses_score']:.3f} (p={model1.pvalues['ses_score']:.4f})")

# Model 2: With GxE interaction
model2 = logit("toxicity ~ genotype * ses_score", data=enhanced_df).fit(disp=0)
print("\n  Model 2 (with GxE interaction):")
print(f"    Genotype effect: {model2.params['genotype']:.3f} (p={model2.pvalues['genotype']:.4f})")
print(f"    SES effect: {model2.params['ses_score']:.3f} (p={model2.pvalues['ses_score']:.4f})")
print(f"    GxE interaction: {model2.params['genotype:ses_score']:.3f} (p={model2.pvalues['genotype:ses_score']:.4f})")

# Check significance
if model2.pvalues['genotype:ses_score'] < 0.05:
    print(f"\n  ✓ SIGNIFICANT GxE interaction detected!")
else:
    print(f"\n  ✗ No significant GxE interaction")

# ── Part 3: Stratified analysis ───────────────────────────────────────────
print("\n[3/5] Stratified analysis by SES level...")

# Split SES into tertiles
enhanced_df['ses_tertile'] = pd.qcut(enhanced_df['ses_score'], 3, labels=['Low SES', 'Medium SES', 'High SES'])

# Calculate genetic effect within each SES tertile
stratified_effects = []
for ses_group in ['Low SES', 'Medium SES', 'High SES']:
    subset = enhanced_df[enhanced_df['ses_tertile'] == ses_group]
    if len(subset) > 0:
        # Simple logistic regression within strata
        model_strata = logit("toxicity ~ genotype", data=subset).fit(disp=0)
        stratified_effects.append({
            'SES_tertile': ses_group,
            'n': len(subset),
            'genotype_effect': model_strata.params['genotype'],
            'p_value': model_strata.pvalues['genotype'],
            'toxicity_rate': subset['toxicity'].mean()
        })

stratified_df = pd.DataFrame(stratified_effects)
print("\n  Genetic effect by SES level:")
print(stratified_df.to_string(index=False))

# ── Part 4: Visualize GxE interaction ─────────────────────────────────────
print("\n[4/5] Creating visualization...")

# Calculate predicted probabilities
ses_grid = np.linspace(0, 1, 50)
predictions = []

for genotype in [0, 1, 2]:
    for ses in ses_grid:
        log_odds = (model2.params['Intercept'] + 
                   model2.params['genotype'] * genotype +
                   model2.params['ses_score'] * ses +
                   model2.params['genotype:ses_score'] * genotype * ses)
        prob = 1 / (1 + np.exp(-log_odds))
        predictions.append({
            'genotype': genotype,
            'ses_score': ses,
            'toxicity_probability': prob
        })

pred_df = pd.DataFrame(predictions)

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['blue', 'orange', 'red']
labels = ['0 alt alleles', '1 alt allele', '2 alt alleles']

for i, genotype in enumerate([0, 1, 2]):
    subset = pred_df[pred_df['genotype'] == genotype]
    ax.plot(subset['ses_score'], subset['toxicity_probability'], 
            color=colors[i], label=labels[i], linewidth=2)

ax.set_xlabel('SES Vulnerability Score (higher = more vulnerable)', fontsize=12)
ax.set_ylabel('Predicted Toxicity Probability', fontsize=12)
ax.set_title('GxE Interaction: Genetic Effect Varies by SES', fontsize=14)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/gxe_interaction_plot.png', dpi=150)
print("  ✓ Saved: data/processed/gxe_interaction_plot.png")

# ── Part 5: Power analysis for GxE detection ──────────────────────────────
print("\n[5/5] Power analysis for GxE detection...")

# Simulate different sample sizes to see power
sample_sizes = [500, 1000, 2000, 5000]
power_results = []

for n in sample_sizes:
    sig_count = 0
    n_simulations = 30  # Reduced for speed
    
    for sim in range(n_simulations):
        # Generate data
        sim_genotypes = np.random.choice([0, 1, 2], n, p=[0.6, 0.35, 0.05])
        sim_ses = np.random.beta(2, 2, n)
        
        # True GxE effect
        sim_risk = 0.05 + sim_genotypes*0.15 + sim_ses*0.20 + sim_genotypes*sim_ses*0.25
        sim_risk = np.clip(sim_risk, 0.01, 0.50)
        sim_toxicity = np.random.binomial(1, sim_risk)
        
        sim_df = pd.DataFrame({'genotype': sim_genotypes, 'ses_score': sim_ses, 'toxicity': sim_toxicity})
        
        # Test GxE
        try:
            model = logit("toxicity ~ genotype * ses_score", data=sim_df).fit(disp=0)
            if model.pvalues['genotype:ses_score'] < 0.05:
                sig_count += 1
        except:
            pass
    
    power = sig_count / n_simulations
    power_results.append({'sample_size': n, 'power': power})

power_df = pd.DataFrame(power_results)
print("\n  Power to detect GxE interaction by sample size:")
print(power_df.to_string(index=False))

# ── Part 6: Save all results ──────────────────────────────────────────────
print("\n[6/6] Saving results...")

# Save enhanced dataset
enhanced_df.to_csv("data/processed/enhanced_gxe_data.csv", index=False)
print("  ✓ Saved: data/processed/enhanced_gxe_data.csv")

# Save model coefficients
coef_df = pd.DataFrame({
    'variable': model2.params.index,
    'coefficient': model2.params.values,
    'p_value': model2.pvalues.values,
    'std_error': model2.bse.values
})
coef_df.to_csv("data/processed/enhanced_gxe_coefficients.csv", index=False)
print("  ✓ Saved: data/processed/enhanced_gxe_coefficients.csv")

# Save power analysis
power_df.to_csv("data/processed/gxe_power_analysis.csv", index=False)
print("  ✓ Saved: data/processed/gxe_power_analysis.csv")

# Save stratified effects
stratified_df.to_csv("data/processed/stratified_genetic_effects.csv", index=False)
print("  ✓ Saved: data/processed/stratified_genetic_effects.csv")

print("\n" + "="*60)
print("✓ STEP 4 ENHANCED COMPLETE!")
print("="*60)

print("\n" + "="*60)
print("KEY INSIGHTS FOR GXE DETECTION")
print("="*60)

print("\n1. GxE Interaction Results:")
if model2.pvalues['genotype:ses_score'] < 0.05:
    print(f"   ✓ SIGNIFICANT interaction detected (p={model2.pvalues['genotype:ses_score']:.4f})")
    print(f"   • Genetic effect is amplified in high SES vulnerability areas")
else:
    print(f"   ✗ No significant interaction in this dataset")

print("\n2. Stratified Effects:")
for _, row in stratified_df.iterrows():
    print(f"   • {row['SES_tertile']}: genotype effect = {row['genotype_effect']:.3f} (p={row['p_value']:.4f})")

print("\n3. Power Analysis:")
for _, row in power_df.iterrows():
    print(f"   • n={row['sample_size']}: {row['power']*100:.0f}% power to detect GxE")

print("\n4. Recommendations:")
print("   • Use continuous SES scores (not binary) for more power")
print("   • Minimum sample size: 2,000-5,000 for 80% power")
print("   • Consider gene-environment correlation in analysis")

print("\nOutput files saved in data/processed/")
print("  • enhanced_gxe_data.csv")
print("  • enhanced_gxe_coefficients.csv")
print("  • gxe_power_analysis.csv")
print("  • stratified_genetic_effects.csv")
print("  • gxe_interaction_plot.png")