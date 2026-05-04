# Step 1A — Genomic Data: 1000 Genomes + gnomAD

import pandas as pd
import numpy as np
import cyvcf2
import requests
import time
import json

# ── Part 3: Load and clean population panel ──────────────────────────────
panel = pd.read_csv("data/raw/genomic/population_panel.panel", sep="\t")
panel = panel[["sample", "pop", "super_pop", "gender"]]

print(panel.head(10))
print("\nSamples per superpopulation:")
print(panel["super_pop"].value_counts())

panel.to_csv("data/processed/population_panel_clean.csv", index=False)
print("\n✓ Saved cleaned panel to data/processed/population_panel_clean.csv")

# ── Part 4: Compute allele frequencies by superpopulation ────────────────
def compute_af_by_population(vcf_path, panel):
    vcf = cyvcf2.VCF(vcf_path)
    samples = pd.Series(vcf.samples)

    sample_pop = samples.map(panel.set_index("sample")["super_pop"])

    superpops = ["AFR", "EUR", "EAS", "SAS", "AMR"]
    pop_indices = {
        pop: np.where(sample_pop == pop)[0]
        for pop in superpops
    }

    records = []
    for variant in vcf:
        gt_types = variant.gt_types

        row = {
            "variant_id": f"{variant.CHROM}_{variant.POS}_{variant.REF}_{variant.ALT[0]}",
            "chrom":      variant.CHROM,
            "pos":        variant.POS,
            "ref":        variant.REF,
            "alt":        variant.ALT[0],
        }

        for pop, idx in pop_indices.items():
            pop_gt = gt_types[idx]
            valid = pop_gt[pop_gt != 2]
            if len(valid) == 0:
                row[f"AF_{pop}"] = np.nan
            else:
                alt_count = np.sum(valid == 1) + np.sum(valid == 3) * 2
                total_alleles = len(valid) * 2
                row[f"AF_{pop}"] = round(alt_count / total_alleles, 4)

        records.append(row)

    return pd.DataFrame(records)

print("\nComputing allele frequencies by population...")
af_df = compute_af_by_population(
    vcf_path="data/raw/genomic/CYP2D6_1kg.vcf.gz",
    panel=panel
)

print(af_df.head(10))
print(f"\nTotal variants processed: {len(af_df)}")

af_df.to_csv("data/processed/CYP2D6_allele_freqs_by_pop.csv", index=False)
print("✓ Saved to data/processed/CYP2D6_allele_freqs_by_pop.csv")

# ── Part 5: Query gnomAD API ──────────────────────────────────────────────
def query_gnomad_gene(gene_symbol):
    url = "https://gnomad.broadinstitute.org/api"
    
    # Fixed query - removed 'af' from populations since it doesn't exist
    query_template = """
    {
      gene(gene_symbol: "%s", reference_genome: GRCh38) {
        variants(dataset: gnomad_r4) {
          variant_id
          pos
          ref
          alt
          genome {
            af
            populations {
              id
              ac
              an
            }
          }
        }
      }
    }
    """
    
    query = query_template % gene_symbol
    
    try:
        response = requests.post(url, json={"query": query}, timeout=60)
    except Exception as e:
        print(f"  Request failed for {gene_symbol}: {e}")
        return pd.DataFrame()
    
    if response.status_code != 200:
        print(f"  Error {response.status_code} for {gene_symbol}")
        if response.status_code == 429:
            print(f"  Rate limited - waiting 10 seconds...")
            time.sleep(10)
            # Retry once
            try:
                response = requests.post(url, json={"query": query}, timeout=60)
                if response.status_code == 200:
                    print(f"  Retry successful!")
                else:
                    return pd.DataFrame()
            except:
                return pd.DataFrame()
        else:
            return pd.DataFrame()
    
    data = response.json()
    
    if "errors" in data:
        print(f"  API error for {gene_symbol}: {data['errors'][0]['message'][:100]}")
        return pd.DataFrame()
    
    variants = data.get("data", {}).get("gene", {}).get("variants", [])
    records = []
    
    for v in variants:
        pop_data = v.get("genome") or {}
        populations = pop_data.get("populations", [])
        overall_af = pop_data.get("af", None)
        
        for pop in populations:
            # Calculate AF from ac and an
            ac = pop.get("ac", 0)
            an = pop.get("an", 0)
            af = ac / an if an > 0 else None
            
            records.append({
                "variant_id":  v["variant_id"],
                "pos":         v["pos"],
                "ref":         v["ref"],
                "alt":         v["alt"],
                "population":  pop["id"],
                "af":          af,
                "ac":          ac,
                "an":          an,
                "af_overall":  overall_af,
                "gene":        gene_symbol
            })
    
    return pd.DataFrame(records)

print("\n" + "="*50)
print("Querying gnomAD API...")
print("="*50)

pharmacogenes = ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "DPYD", "CYP2B6", "HLA-B"]
all_results = []

for gene in pharmacogenes:
    print(f"  Querying gnomAD for {gene}...")
    df = query_gnomad_gene(gene)
    if not df.empty:
        all_results.append(df)
        print(f"  ✓ {gene}: {df['variant_id'].nunique()} variants, {len(df)} rows")
    else:
        print(f"  ✗ {gene}: no data returned")
    time.sleep(5)

if all_results:
    gnomad_df = pd.concat(all_results, ignore_index=True)
    print(f"\nTotal rows: {len(gnomad_df):,}")
    print(f"Unique variants: {gnomad_df['variant_id'].nunique():,}")
    print(f"Populations: {sorted(gnomad_df['population'].unique())}")

    gnomad_df.to_csv("data/processed/pharmacogenes_gnomad_freqs.csv", index=False)
    print("\n✓ Saved to data/processed/pharmacogenes_gnomad_freqs.csv")
else:
    print("\n✗ No gnomAD data retrieved")

print("\n✓ Step 1A complete!")