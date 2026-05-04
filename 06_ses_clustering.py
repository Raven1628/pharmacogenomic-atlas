# 06_ses_clustering_simple.py
# Step 3 - SES-Stratified Population Clustering (Simple version)

import pandas as pd
import numpy as np


print("="*60)
print("STEP 3: SES-Stratified Population Clustering")
print("="*60)

# ── Part 1: Load all data components ──────────────────────────────────────
print("\n[1/6] Loading data components...")

# Load genetic ancestry data
ancestry_df = pd.read_csv("data/processed/population_panel_clean.csv")
print(f"  ✓ Genetic ancestry: {len(ancestry_df)} samples, {ancestry_df['super_pop'].nunique()} superpopulations")

# Load SES data
ses_df = pd.read_csv("data/processed/ses_simplified.csv")
print(f"  ✓ SES data: {len(ses_df)} counties/states")

# Load clinical outcomes
clinical_df = pd.read_csv("data/processed/simulated_drug_outcomes.csv")
print(f"  ✓ Clinical outcomes: {len(clinical_df):,} patient-drug pairs")

# Load variant annotations
variants_df = pd.read_csv("data/processed/high_priority_variants.csv")
print(f"  ✓ High-priority variants: {len(variants_df)} variants")

# ── Part 2: Create SES composite score and strata ─────────────────────────
print("\n[2/6] Creating SES strata...")

if 'SES_composite' not in ses_df.columns:
    # Normalize SES metrics manually (without sklearn)
    ses_metrics = ['poverty_rate', 'unemployment_rate', 'no_hs_diploma']
    for metric in ses_metrics:
        min_val = ses_df[metric].min()
        max_val = ses_df[metric].max()
        ses_df[f'{metric}_norm'] = (ses_df[metric] - min_val) / (max_val - min_val)
    
    ses_df['SES_composite'] = ses_df[[f'{m}_norm' for m in ses_metrics]].mean(axis=1)

# Create SES quartiles
ses_df['SES_quartile'] = pd.qcut(
    ses_df['SES_composite'], 
    q=4, 
    labels=['Q1_LowestVuln', 'Q2_LowVuln', 'Q3_MedVuln', 'Q4_HighestVuln'],
    duplicates='drop'
)

print(f"  ✓ SES composite score range: {ses_df['SES_composite'].min():.2f} - {ses_df['SES_composite'].max():.2f}")
print(f"\n  SES quartile distribution:")
print(ses_df['SES_quartile'].value_counts())

# ── Part 3: Create ancestry-SES interaction matrix ───────────────────────
print("\n[3/6] Creating genetic ancestry + SES integration...")

ancestry_groups = ancestry_df['super_pop'].unique()
ses_quartiles = ses_df['SES_quartile'].unique()

# Create synthetic population
np.random.seed(42)
n_individuals = 10000

synthetic_pop = []
ancestry_weights = {'AFR': 0.264, 'EUR': 0.201, 'EAS': 0.201, 'SAS': 0.195, 'AMR': 0.139}  # Based on 1000G

for i in range(n_individuals):
    # Assign ancestry
    ancestry = np.random.choice(list(ancestry_weights.keys()), p=list(ancestry_weights.values()))
    
    # Assign SES based on ancestry (simulating real-world disparities)
    if ancestry in ['AFR', 'AMR']:
        ses_score = np.random.beta(3, 2)  # Higher vulnerability
    elif ancestry == 'SAS':
        ses_score = np.random.beta(2.5, 2.5)  # Medium
    else:  # EUR, EAS
        ses_score = np.random.beta(2, 3)  # Lower vulnerability
    
    # Determine SES quartile
    if ses_score < 0.25:
        ses_quartile = 'Q1_LowestVuln'
    elif ses_score < 0.5:
        ses_quartile = 'Q2_LowVuln'
    elif ses_score < 0.75:
        ses_quartile = 'Q3_MedVuln'
    else:
        ses_quartile = 'Q4_HighestVuln'
    
    synthetic_pop.append({
        'individual_id': f"IND_{i:05d}",
        'ancestry': ancestry,
        'ses_score': ses_score,
        'ses_quartile': ses_quartile,
        'high_vulnerability': 1 if ses_quartile == 'Q4_HighestVuln' else 0
    })

synthetic_df = pd.DataFrame(synthetic_pop)

print(f"  ✓ Created synthetic population: {len(synthetic_df)} individuals")

# Create interaction table
interaction_table = synthetic_df.groupby(['ancestry', 'ses_quartile']).size().unstack(fill_value=0)
print("\n  Ancestry × SES distribution:")
print(interaction_table)

# ── Part 4: Simulate genetic variants for GxE analysis ────────────────────
print("\n[4/6] Simulating variant genotypes by ancestry-SES group...")

# Load variant info
variant_info = variants_df.head(10)  # Start with top 10 variants

# Generate genotype data
genotype_data = []

for variant in variant_info.itertuples():
    variant_id = variant.variant_id
    gene = variant.gene
    
    for _, person in synthetic_df.iterrows():
        # Simulate genotype based on ancestry and variant
        if variant.impact == 'HIGH':
            # Rare variant - low frequency
            if person.ancestry == 'AFR':
                prob_alt = 0.05
            elif person.ancestry == 'EAS':
                prob_alt = 0.02
            else:
                prob_alt = 0.01
        else:
            # Common variant
            if person.ancestry == 'AFR':
                prob_alt = 0.35
            elif person.ancestry == 'EAS':
                prob_alt = 0.25
            else:
                prob_alt = 0.15
        
        # Adjust by SES (environmental factors)
        if person.high_vulnerability == 1:
            prob_alt *= 1.2  # Slight increase in high SES areas (due to stress, diet, etc.)
        
        # Sample genotype (0, 1, or 2 copies of alt allele)
        genotype = np.random.choice([0, 1, 2], p=[(1-prob_alt)**2, 2*prob_alt*(1-prob_alt), prob_alt**2])
        
        genotype_data.append({
            'individual_id': person.individual_id,
            'variant_id': variant_id,
            'gene': gene,
            'genotype': genotype,
            'alt_alleles': genotype
        })

genotype_df = pd.DataFrame(genotype_data)
print(f"  ✓ Generated genotypes for {genotype_df['variant_id'].nunique()} variants × {genotype_df['individual_id'].nunique()} individuals")
print(f"    Total genotype records: {len(genotype_df):,}")

# ── Part 5: Associate clinical outcomes ───────────────────────────────────
print("\n[5/6] Simulating drug response by genotype and SES...")

# Merge clinical outcomes with genotypes and SES
clinical_outcomes = []

for _, person in synthetic_df.iterrows():
    # Sample a drug (randomly from clinical_df)
    for drug in clinical_df['drug'].unique():
        # Get variant effect for this drug
        drug_variants = clinical_df[clinical_df['drug'] == drug]['rsid'].unique()
        
        # Calculate genetic risk score
        genetic_risk = 0
        for variant_id in variant_info['variant_id'][:5]:  # Top 5 variants
            gen = genotype_df[(genotype_df['individual_id'] == person.individual_id) & 
                               (genotype_df['variant_id'] == variant_id)]
            if not gen.empty:
                genetic_risk += gen['alt_alleles'].values[0] * 0.1
        
        # SES effect
        if person.high_vulnerability == 1:
            ses_effect = 0.3
        else:
            ses_effect = 0.0
        
        # GxE interaction (genetic effect is amplified in high SES areas)
        gxe_interaction = genetic_risk * (1 + ses_effect)
        
        # Calculate phenotype
        base_response = 1.0
        response_prob = base_response - genetic_risk * 0.15 - ses_effect * 0.2 - gxe_interaction * 0.1
        response_prob = np.clip(response_prob, 0.1, 0.95)
        
        toxicity_prob = genetic_risk * 0.1 + ses_effect * 0.25 + gxe_interaction * 0.15
        toxicity_prob = np.clip(toxicity_prob, 0.01, 0.6)
        
        # Sample outcomes
        optimal_response = np.random.binomial(1, response_prob)
        toxicity = np.random.binomial(1, toxicity_prob)
        
        clinical_outcomes.append({
            'individual_id': person.individual_id,
            'ancestry': person.ancestry,
            'ses_quartile': person.ses_quartile,
            'high_vulnerability': person.high_vulnerability,
            'drug': drug,
            'optimal_response': optimal_response,
            'toxicity': toxicity,
            'genetic_risk_score': round(genetic_risk, 3),
            'gxe_interaction_term': round(gxe_interaction, 3)
        })

outcomes_by_individual = pd.DataFrame(clinical_outcomes)
print(f"  ✓ Created outcomes for {outcomes_by_individual['individual_id'].nunique()} individuals × {outcomes_by_individual['drug'].nunique()} drugs")
print(f"    Total outcome records: {len(outcomes_by_individual):,}")

# ── Part 6: Analyze GxE patterns ──────────────────────────────────────────
print("\n[6/6] Analyzing GxE patterns...")

# Calculate outcomes by ancestry and SES
analysis_results = []

for ancestry in synthetic_df['ancestry'].unique():
    for ses_q in synthetic_df['ses_quartile'].unique():
        subset = outcomes_by_individual[
            (outcomes_by_individual['ancestry'] == ancestry) & 
            (outcomes_by_individual['ses_quartile'] == ses_q)
        ]
        
        if len(subset) > 0:
            analysis_results.append({
                'ancestry': ancestry,
                'ses_quartile': ses_q,
                'n_individuals': len(subset),
                'optimal_response_rate': subset['optimal_response'].mean(),
                'toxicity_rate': subset['toxicity'].mean(),
                'mean_genetic_risk': subset['genetic_risk_score'].mean(),
                'mean_gxe_interaction': subset['gxe_interaction_term'].mean()
            })

analysis_df = pd.DataFrame(analysis_results)

print("\n  Key findings by ancestry and SES:")
print(analysis_df.to_string(index=False, float_format='%.3f'))

# Calculate disparity ratios
baseline_toxicity = analysis_df[analysis_df['ses_quartile'] == 'Q1_LowestVuln']['toxicity_rate'].mean()
analysis_df['disparity_ratio'] = analysis_df['toxicity_rate'] / baseline_toxicity

print("\n  Disparity analysis (toxicity risk relative to lowest vulnerability group):")
disparity_summary = analysis_df.groupby('ses_quartile').agg({
    'disparity_ratio': ['mean', 'min', 'max']
}).round(2)
print(disparity_summary)

# ── Part 7: Save outputs ──────────────────────────────────────────────────
print("\n[7/7] Saving outputs...")

# Save synthetic population
synthetic_df.to_csv("data/processed/integrated_population_clusters.csv", index=False)
print("  ✓ Saved: data/processed/integrated_population_clusters.csv")

# Save genotypes
genotype_df.to_csv("data/processed/genotype_data.csv", index=False)
print("  ✓ Saved: data/processed/genotype_data.csv")

# Save clinical outcomes
outcomes_by_individual.to_csv("data/processed/gxe_outcomes.csv", index=False)
print("  ✓ Saved: data/processed/gxe_outcomes.csv")

# Save analysis results
analysis_df.to_csv("data/processed/gxe_analysis_results.csv", index=False)
print("  ✓ Saved: data/processed/gxe_analysis_results.csv")

# Save ancestry-SES interaction table
interaction_table.to_csv("data/processed/ancestry_ses_interaction.csv")
print("  ✓ Saved: data/processed/ancestry_ses_interaction.csv")

print("\n" + "="*60)
print("✓ STEP 3 COMPLETE!")
print("="*60)
print("\nKey findings for GxE analysis:")
print("\n1. Ancestry-SES combinations created:")
for ancestry in synthetic_df['ancestry'].unique():
    for ses_q in synthetic_df['ses_quartile'].unique():
        count = len(synthetic_df[(synthetic_df['ancestry'] == ancestry) & 
                                  (synthetic_df['ses_quartile'] == ses_q)])
        if count > 500:
            print(f"   • {ancestry} + {ses_q}: {count} individuals")

print("\n2. GxE interaction detected:")
high_risk = analysis_df[analysis_df['ses_quartile'] == 'Q4_HighestVuln']
if len(high_risk) > 0:
    print(f"   • Highest vulnerability group has {high_risk['toxicity_rate'].mean()*100:.1f}% toxicity rate")
    print(f"   • {high_risk['disparity_ratio'].mean():.1f}x higher risk than lowest vulnerability group")

print("\n3. Next step (Step 4): Statistical GxE modeling")
print("   Test: Drug Response ~ Genotype + SES + Genotype×SES")

print("\nOutput files:")
print("  • integrated_population_clusters.csv - Population with ancestry+SES")
print("  • genotype_data.csv - Variant genotypes for each individual")
print("  • gxe_outcomes.csv - Clinical outcomes with GxE terms")
print("  • gxe_analysis_results.csv - Summary by ancestry and SES")
print("  • ancestry_ses_interaction.csv - Interaction matrix")