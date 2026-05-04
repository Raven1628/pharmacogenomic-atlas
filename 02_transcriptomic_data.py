# 02_transcriptomic_data.py
# Step 1B - Transcriptomic Data: GTEx

import pandas as pd
import urllib.request
import os
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 1B: Downloading GTEx Transcriptomic Data")
print("="*60)

# ── Part 1: Create directories ─────────────────────────────────────────────
os.makedirs("data/raw/transcriptomic", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# ── Part 2: Download GTEx files ───────────────────────────────────────────
print("\n[1/3] Downloading GTEx files...")

# File 1: Gene median TPM expression by tissue (~30MB)
gtex_median_url = "https://storage.googleapis.com/adult-gtex/bulk-gex/v10/rna-seq/GTEx_Analysis_v10_RNASeQCv2.4.2_gene_median_tpm.gct.gz"
gtex_median_file = "data/raw/transcriptomic/GTEx_median_tpm.gct.gz"

if not os.path.exists(gtex_median_file):
    print(f"  Downloading GTEx median expression data...")
    urllib.request.urlretrieve(gtex_median_url, gtex_median_file)
    print(f"  ✓ Downloaded to {gtex_median_file}")
else:
    print(f"  ✓ File already exists: {gtex_median_file}")

# File 2: Sample attributes (to know which samples are from which tissues)
gtex_annot_url = "https://storage.googleapis.com/adult-gtex/annotations/v10/metadata-files/GTEx_Analysis_v10_Annotations_SampleAttributesDS.txt"
gtex_annot_file = "data/raw/transcriptomic/GTEx_sample_attributes.txt"

if not os.path.exists(gtex_annot_file):
    print(f"  Downloading GTEx sample annotations...")
    urllib.request.urlretrieve(gtex_annot_url, gtex_annot_file)
    print(f"  ✓ Downloaded to {gtex_annot_file}")
else:
    print(f"  ✓ File already exists: {gtex_annot_file}")

# ── Part 3: Load and parse GTEx data ──────────────────────────────────────
print("\n[2/3] Loading GTEx data...")

# Load the gene expression data (skip first 2 rows which are metadata)
print("  Loading median TPM expression...")
gtex_expr = pd.read_csv(
    gtex_median_file,
    sep="\t",
    skiprows=2,
    compression="gzip"
)

print(f"  ✓ Loaded {len(gtex_expr)} genes × {len(gtex_expr.columns)-2} tissues")

# Load sample attributes (suppress dtype warning)
print("  Loading sample annotations...")
gtex_annot = pd.read_csv(gtex_annot_file, sep="\t", low_memory=False)

# Extract tissue type from SMTSD column
gtex_annot['tissue'] = gtex_annot['SMTSD'].str.extract(r'(.+?) - ')[0]
print(f"  ✓ Found {gtex_annot['tissue'].nunique()} unique tissue types")

# ── Part 4: Filter to pharmacogenes of interest ───────────────────────────
print("\n[3/4] Filtering to pharmacogenes...")

pharmacogenes = ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "DPYD", "CYP2B6"]

# Filter expression data to just these genes
gtex_pharma = gtex_expr[gtex_expr['Description'].isin(pharmacogenes)]

print(f"  ✓ Found {len(gtex_pharma)} pharmacogenes in GTEx")
print(f"  Genes found: {sorted(gtex_pharma['Description'].tolist())}")

# Display initial summary
print("\n  Summary of pharmacogene expression (top tissues):")
for idx, row in gtex_pharma.iterrows():
    gene = row['Description']
    expr_data = {}
    for col in gtex_expr.columns[2:]:
        try:
            value = float(row[col])
            if value > 0:
                tissue_clean = col.split(' - ')[0] if ' - ' in col else col
                expr_data[tissue_clean] = value
        except (ValueError, TypeError):
            continue
    
    if expr_data:
        top_tissues = sorted(expr_data.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"    {gene}:")
        for tissue, value in top_tissues:
            print(f"      - {tissue}: {value:.2f} TPM")

# ── Part 5: Create tissue expression matrix ────────────────────────────────
print("\n[4/4] Creating tissue expression matrix...")

# Extract all tissue columns
all_tissue_cols = gtex_expr.columns[2:]

# Build expression records
expression_records = []
for idx, row in gtex_pharma.iterrows():
    gene = row['Description']
    for tissue_col in all_tissue_cols:
        try:
            tpm = float(row[tissue_col])
            if tpm > 0:
                tissue_clean = tissue_col.split(' - ')[0] if ' - ' in tissue_col else tissue_col
                expression_records.append({
                    'gene': gene,
                    'tissue': tissue_clean,
                    'tpm': tpm
                })
        except (ValueError, TypeError):
            continue

# Convert to DataFrame
expression_df = pd.DataFrame(expression_records)

print(f"  ✓ Found {len(expression_df)} gene-tissue pairs with expression > 0")
print(f"  ✓ {expression_df['tissue'].nunique()} unique tissues")

# Show summary by gene
print("\n  Summary by gene (all tissues with expression > 0):")
for gene in pharmacogenes:
    gene_data = expression_df[expression_df['gene'] == gene]
    if not gene_data.empty:
        top_tissues = gene_data.nlargest(3, 'tpm')
        print(f"    {gene}: {len(gene_data)} tissues with expression")
        for _, row in top_tissues.iterrows():
            print(f"      - {row['tissue']}: {row['tpm']:.2f} TPM")

# Create matrix format
expression_matrix = expression_df.pivot_table(
    index='gene',
    columns='tissue',
    values='tpm',
    fill_value=0
)

# Save outputs
print("\n[5/5] Saving outputs...")
expression_matrix.to_csv("data/processed/gtex_pharmacogene_expression_matrix.csv")
print("  ✓ Saved: data/processed/gtex_pharmacogene_expression_matrix.csv")

expression_df.to_csv("data/processed/gtex_expression_long.csv", index=False)
print("  ✓ Saved: data/processed/gtex_expression_long.csv")

tissue_counts = gtex_annot['tissue'].value_counts().reset_index()
tissue_counts.columns = ['tissue', 'n_samples']
tissue_counts.to_csv("data/processed/gtex_tissue_sample_counts.csv", index=False)
print("  ✓ Saved: data/processed/gtex_tissue_sample_counts.csv")

print("\n" + "="*60)
print("✓ STEP 1B COMPLETE!")
print("="*60)
print("\nOutput files:")
print("  • data/processed/gtex_pharmacogene_expression_matrix.csv")
print("  • data/processed/gtex_expression_long.csv")
print("  • data/processed/gtex_tissue_sample_counts.csv")
