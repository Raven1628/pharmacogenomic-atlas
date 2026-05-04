# 04_clinical_data.py
# Step 1D - Clinical Outcomes: GWAS Summary Statistics (LARGER DATASET)

import pandas as pd
import urllib.request
import os
import json
import time
import numpy as np

print("="*60)
print("STEP 1D: Downloading GWAS Clinical Data (LARGE DATASET)")
print("="*60)

# ── Part 1: Create directories ─────────────────────────────────────────────
os.makedirs("data/raw/gwas", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# ── Part 2: Define pharmacogenes and relevant drug responses ──────────────
print("\n[1/5] Identifying relevant GWAS studies...")

# EXPANDED drug-gene pairs
drug_gene_pairs = {
    "CYP2C9": {
        "drug": "Warfarin",
        "phenotype": "Warfarin dose requirement",
        "gwas_id": "GCST002227",
        "description": "Warfarin maintenance dose"
    },
    "CYP2C19": {
        "drug": "Clopidogrel",
        "phenotype": "Clopidogrel response",
        "gwas_id": "GCST003140",
        "description": "Platelet aggregation response"
    },
    "SLCO1B1": {
        "drug": "Simvastatin",
        "phenotype": "Statin-induced myopathy",
        "gwas_id": "GCST001899",
        "description": "Creatine kinase levels"
    },
    "DPYD": {
        "drug": "Fluorouracil",
        "phenotype": "Fluorouracil toxicity",
        "gwas_id": "GCST006318",
        "description": "Drug-induced toxicity"
    },
    "CYP2D6": {
        "drug": "Codeine",
        "phenotype": "Codeine toxicity",
        "gwas_id": "GCST002228",
        "description": "Respiratory depression risk"
    },
    "CYP2D6": {
        "drug": "Tamoxifen",
        "phenotype": "Tamoxifen efficacy",
        "gwas_id": "GCST002229",
        "description": "Breast cancer recurrence"
    },
    "HLA-B": {
        "drug": "Carbamazepine",
        "phenotype": "SJS/TEN",
        "gwas_id": "GCST001360",
        "description": "Severe skin reaction"
    },
    "HLA-B": {
        "drug": "Allopurinol",
        "phenotype": "SCAR",
        "gwas_id": "GCST001361",
        "description": "Hypersensitivity"
    }
}

for gene, info in drug_gene_pairs.items():
    print(f"  {gene} → {info['drug']}: {info['phenotype']}")

# ── Part 3: Create LARGE simulated GWAS data ──────────────────────────────
print("\n[2/5] Creating LARGE simulated GWAS summary statistics...")
print("  (Based on known pharmacogenetic variants from literature)")

np.random.seed(42)

# EXPANDED known pharmacogenetic variants
known_variants = {
    "CYP2C9": [
        {"rsid": "rs1799853", "variant": "CYP2C9*2", "effect_size": -0.35, "p_value": 2.1e-12, "effect_allele": "T"},
        {"rsid": "rs1057910", "variant": "CYP2C9*3", "effect_size": -0.42, "p_value": 3.4e-15, "effect_allele": "C"},
        {"rsid": "rs9332239", "variant": "CYP2C9*6", "effect_size": -0.28, "p_value": 1.2e-8, "effect_allele": "A"},
        {"rsid": "rs28371686", "variant": "CYP2C9*5", "effect_size": -0.31, "p_value": 5.6e-9, "effect_allele": "C"},
        {"rsid": "rs9332131", "variant": "CYP2C9*11", "effect_size": -0.25, "p_value": 2.3e-7, "effect_allele": "A"}
    ],
    "CYP2C19": [
        {"rsid": "rs4244285", "variant": "CYP2C19*2", "effect_size": -0.38, "p_value": 5.6e-14, "effect_allele": "G"},
        {"rsid": "rs4986893", "variant": "CYP2C19*3", "effect_size": -0.31, "p_value": 2.3e-10, "effect_allele": "A"},
        {"rsid": "rs12248560", "variant": "CYP2C19*17", "effect_size": 0.25, "p_value": 1.8e-7, "effect_allele": "C"},
        {"rsid": "rs17884712", "variant": "CYP2C19*4", "effect_size": -0.22, "p_value": 3.4e-6, "effect_allele": "A"},
        {"rsid": "rs56337013", "variant": "CYP2C19*8", "effect_size": -0.19, "p_value": 4.5e-5, "effect_allele": "T"}
    ],
    "SLCO1B1": [
        {"rsid": "rs4149056", "variant": "SLCO1B1*5", "effect_size": 0.52, "p_value": 8.7e-18, "effect_allele": "C"},
        {"rsid": "rs2306283", "variant": "SLCO1B1*1a", "effect_size": -0.18, "p_value": 2.1e-5, "effect_allele": "G"},
        {"rsid": "rs4149081", "variant": "SLCO1B1*15", "effect_size": 0.45, "p_value": 1.2e-12, "effect_allele": "T"},
        {"rsid": "rs11045819", "variant": "SLCO1B1*17", "effect_size": 0.38, "p_value": 3.4e-10, "effect_allele": "A"}
    ],
    "DPYD": [
        {"rsid": "rs3918290", "variant": "DPYD*2A", "effect_size": 0.89, "p_value": 1.2e-22, "effect_allele": "A"},
        {"rsid": "rs55886062", "variant": "DPYD*13", "effect_size": 0.67, "p_value": 3.4e-14, "effect_allele": "A"},
        {"rsid": "rs67376798", "variant": "DPYD*9B", "effect_size": 0.34, "p_value": 4.5e-8, "effect_allele": "T"},
        {"rsid": "rs75017182", "variant": "DPYD*4", "effect_size": 0.41, "p_value": 2.1e-9, "effect_allele": "G"}
    ],
    "CYP2D6": [
        {"rsid": "rs3892097", "variant": "CYP2D6*4", "effect_size": 0.45, "p_value": 1.2e-15, "effect_allele": "C"},
        {"rsid": "rs1065852", "variant": "CYP2D6*10", "effect_size": 0.32, "p_value": 2.3e-11, "effect_allele": "T"},
        {"rsid": "rs5030655", "variant": "CYP2D6*3", "effect_size": 0.38, "p_value": 5.6e-12, "effect_allele": "A"},
        {"rsid": "rs1135840", "variant": "CYP2D6*41", "effect_size": 0.28, "p_value": 3.4e-9, "effect_allele": "C"}
    ],
    "HLA-B": [
        {"rsid": "rs2395029", "variant": "HLA-B*57:01", "effect_size": 5.20, "p_value": 5.4e-25, "effect_allele": "G"},
        {"rsid": "rs2844682", "variant": "HLA-B*15:02", "effect_size": 4.80, "p_value": 2.1e-20, "effect_allele": "T"},
        {"rsid": "rs9263726", "variant": "HLA-B*58:01", "effect_size": 4.50, "p_value": 1.8e-18, "effect_allele": "A"}
    ]
}

# Create summary statistics
gwas_results = []
for gene, variants in known_variants.items():
    drug_info = drug_gene_pairs.get(gene, {"drug": "Unknown", "phenotype": "Unknown"})
    for variant in variants:
        beta_se = abs(variant["effect_size"]) / 3
        z_score = variant["effect_size"] / beta_se
        gwas_results.append({
            "gene": gene,
            "drug": drug_info["drug"],
            "phenotype": drug_info["phenotype"],
            "rsid": variant["rsid"],
            "variant_name": variant["variant"],
            "effect_allele": variant["effect_allele"],
            "beta": variant["effect_size"],
            "se": beta_se,
            "z_score": z_score,
            "p_value": variant["p_value"],
            "direction": "decreased_response" if variant["effect_size"] < 0 else "increased_toxicity"
        })

gwas_df = pd.DataFrame(gwas_results)
print(f"  ✓ Created GWAS summary statistics for {gwas_df['gene'].nunique()} genes")
print(f"  ✓ Total associations: {len(gwas_df)}")

# ── Part 4: Create LARGE simulated outcomes ───────────────────────────────
print("\n[3/5] Creating LARGE simulated individual-level outcomes...")

np.random.seed(123)
n_patients = 50000  # INCREASED from 10,000 to 50,000

print(f"  Simulating {n_patients:,} patients...")

patient_ids = [f"P_{i:06d}" for i in range(n_patients)]

# Simulate outcomes
simulated_outcomes = []
for idx, row in gwas_df.iterrows():
    gene = row['gene']
    rsid = row['rsid']
    beta = row['beta']
    
    if rsid in ["rs4149056", "rs3918290"]:
        genotype_freqs = [0.85, 0.13, 0.02]
    elif rsid in ["rs2395029", "rs2844682"]:
        genotype_freqs = [0.95, 0.05, 0.00]  # HLA alleles are rarer
    else:
        genotype_freqs = [0.45, 0.42, 0.13]
    
    genotypes = np.random.choice([0, 1, 2], n_patients, p=genotype_freqs)
    baseline = 100
    genetic_effect = genotypes * beta * 20
    env_noise = np.random.normal(0, 15, n_patients)
    phenotype = np.clip(baseline + genetic_effect + env_noise, 20, 200)
    toxicity_threshold = baseline + 50
    toxicity = (phenotype > toxicity_threshold).astype(int)
    
    for i in range(n_patients):
        simulated_outcomes.append({
            'patient_id': patient_ids[i],
            'gene': gene,
            'drug': row['drug'],
            'rsid': rsid,
            'genotype_dosage': genotypes[i],
            'phenotype_continuous': round(phenotype[i], 2),
            'toxicity_binary': toxicity[i],
            'response_optimal': 1 if (phenotype[i] > 40 and phenotype[i] < 160) else 0
        })

outcomes_df = pd.DataFrame(simulated_outcomes)
print(f"  ✓ Created simulated outcomes for {outcomes_df['patient_id'].nunique():,} patients")
print(f"  ✓ Total records: {len(outcomes_df):,}")

# ── Part 5: Save outputs ──────────────────────────────────────────────────
print("\n[4/5] Saving outputs...")

gwas_df.to_csv("data/processed/gwas_summary_stats.csv", index=False)
outcomes_df.to_csv("data/processed/simulated_drug_outcomes.csv", index=False)

variant_phenotype = gwas_df[['gene', 'drug', 'rsid', 'variant_name', 'beta', 'p_value', 'direction']].copy()
variant_phenotype.to_csv("data/processed/variant_phenotype_mapping.csv", index=False)

print("  ✓ Saved all outputs")

print("\n" + "="*60)
print("✓ STEP 1D COMPLETE!")
print(f"  • Generated {n_patients:,} patient records")
print(f"  • {len(gwas_df)} variant associations")
print("="*60)
