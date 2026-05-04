# pca_complete_analysis.py
# Complete PCA Analysis for Pharmacogenomic Equity Atlas
# Run this once to generate all PCA visualizations

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("COMPLETE PCA ANALYSIS FOR PHARMACOGENOMIC EQUITY ATLAS")
print("="*60)

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("Set2")

# Create output directory
import os
os.makedirs('data/processed/figures', exist_ok=True)

# ============================================================
# 1. LOAD ALL DATA
# ============================================================
print("\n[1/6] Loading data...")

# Load equity scores
df_equity = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded equity scores: {len(df_equity)} records")

# Load GxE data
df_gxe = pd.read_csv("data/processed/enhanced_gxe_data.csv")
print(f"  ✓ Loaded GxE data: {len(df_gxe)} records")

# Load genotype data
df_genotype = pd.read_csv("data/processed/genotype_data.csv")
print(f"  ✓ Loaded genotype data: {len(df_genotype)} records")

# Load ancestry labels
df_ancestry = pd.read_csv("data/processed/integrated_population_clusters.csv")
print(f"  ✓ Loaded ancestry labels: {len(df_ancestry)} records")

# ============================================================
# 2. GENETIC ANCESTRY PCA
# ============================================================
print("\n[2/6] Creating Genetic Ancestry PCA...")

# Create genotype matrix
genotype_matrix = df_genotype.pivot_table(
    index='individual_id', 
    columns='variant_id', 
    values='alt_alleles', 
    fill_value=0
)

# Match samples with ancestry
common_samples = list(set(genotype_matrix.index) & set(df_ancestry['individual_id']))
X_geno = genotype_matrix.loc[common_samples]
y_ancestry = df_ancestry.set_index('individual_id').loc[common_samples, 'ancestry']

# PCA
scaler_geno = StandardScaler()
X_geno_scaled = scaler_geno.fit_transform(X_geno)
pca_geno = PCA(n_components=2)
pca_geno_result = pca_geno.fit_transform(X_geno_scaled)

# Create plot
fig, ax = plt.subplots(figsize=(10, 8))
colors_ancestry = {'AFR': '#e41a1c', 'EUR': '#377eb8', 'EAS': '#4daf4a', 
                   'SAS': '#984ea3', 'AMR': '#ff7f00'}

for ancestry in y_ancestry.unique():
    mask = y_ancestry == ancestry
    ax.scatter(pca_geno_result[mask, 0], pca_geno_result[mask, 1], 
               c=colors_ancestry[ancestry], label=ancestry, alpha=0.6, s=30, edgecolors='white', linewidth=0.5)

ax.set_xlabel(f'PC1 ({pca_geno.explained_variance_ratio_[0]*100:.1f}%)', fontsize=12)
ax.set_ylabel(f'PC2 ({pca_geno.explained_variance_ratio_[1]*100:.1f}%)', fontsize=12)
ax.set_title('Genetic Ancestry PCA - 1000 Genomes Populations', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_genetic_ancestry.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/pca_genetic_ancestry.pdf', bbox_inches='tight')
print("  ✓ Saved: pca_genetic_ancestry.png/pdf")

# ============================================================
# 3. SES vs EQUITY SCORE PCA
# ============================================================
print("\n[3/6] Creating SES vs Equity Score PCA...")

# Prepare features
features_ses = ['genetic_risk', 'ses_risk', 'equity_score']
X_ses = df_equity[features_ses]

# Standardize
scaler_ses = StandardScaler()
X_ses_scaled = scaler_ses.fit_transform(X_ses)

# PCA
pca_ses = PCA(n_components=2)
pca_ses_result = pca_ses.fit_transform(X_ses_scaled)

# Create 2-panel figure
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Colored by ancestry
ax1 = axes[0]
for ancestry in df_equity['ancestry'].unique():
    mask = df_equity['ancestry'] == ancestry
    ax1.scatter(pca_ses_result[mask, 0], pca_ses_result[mask, 1], 
                c=colors_ancestry[ancestry], label=ancestry, alpha=0.5, s=20)
ax1.set_xlabel(f'PC1 ({pca_ses.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
ax1.set_ylabel(f'PC2 ({pca_ses.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
ax1.set_title('A: Risk Components by Ancestry', fontsize=12, fontweight='bold')
ax1.legend(loc='best', fontsize=9)
ax1.grid(True, alpha=0.3)

# Panel B: Colored by risk category
ax2 = axes[1]
risk_colors = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
               'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}

for risk, color in risk_colors.items():
    mask = df_equity['risk_category'] == risk
    ax2.scatter(pca_ses_result[mask, 0], pca_ses_result[mask, 1], 
                c=color, label=risk, alpha=0.5, s=20)
ax2.set_xlabel(f'PC1 ({pca_ses.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
ax2.set_ylabel(f'PC2 ({pca_ses.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
ax2.set_title('B: Risk Components by Risk Category', fontsize=12, fontweight='bold')
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_ses_equity.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/pca_ses_equity.pdf', bbox_inches='tight')
print("  ✓ Saved: pca_ses_equity.png/pdf")

# ============================================================
# 4. GxE INTERACTION PCA
# ============================================================
print("\n[4/6] Creating GxE Interaction PCA...")

# Prepare features
df_gxe['risk_category'] = pd.cut(df_gxe['toxicity'], bins=[-0.1, 0.5, 1.1], 
                                  labels=['Low Toxicity', 'High Toxicity'])
df_gxe['ses_tertile'] = pd.qcut(df_gxe['ses_score'], 3, labels=['Low SES', 'Medium SES', 'High SES'])

features_gxe = ['genotype', 'ses_score', 'toxicity']
X_gxe = df_gxe[features_gxe]

# Standardize
scaler_gxe = StandardScaler()
X_gxe_scaled = scaler_gxe.fit_transform(X_gxe)

# PCA
pca_gxe = PCA(n_components=2)
pca_gxe_result = pca_gxe.fit_transform(X_gxe_scaled)

# Create 2x2 panel
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: By genotype
ax1 = axes[0, 0]
for gt in [0, 1, 2]:
    mask = df_gxe['genotype'] == gt
    ax1.scatter(pca_gxe_result[mask, 0], pca_gxe_result[mask, 1], 
                label=f'{gt} alt alleles', alpha=0.5, s=20)
ax1.set_xlabel(f'PC1 ({pca_gxe.explained_variance_ratio_[0]*100:.1f}%)')
ax1.set_ylabel(f'PC2 ({pca_gxe.explained_variance_ratio_[1]*100:.1f}%)')
ax1.set_title('A: By Genotype', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: By SES tertile
ax2 = axes[0, 1]
ses_colors = {'Low SES': '#27ae60', 'Medium SES': '#f39c12', 'High SES': '#e74c3c'}
for ses, color in ses_colors.items():
    mask = df_gxe['ses_tertile'] == ses
    ax2.scatter(pca_gxe_result[mask, 0], pca_gxe_result[mask, 1], 
                c=color, label=ses, alpha=0.5, s=20)
ax2.set_xlabel(f'PC1 ({pca_gxe.explained_variance_ratio_[0]*100:.1f}%)')
ax2.set_ylabel(f'PC2 ({pca_gxe.explained_variance_ratio_[1]*100:.1f}%)')
ax2.set_title('B: By SES Level', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: By toxicity
ax3 = axes[1, 0]
tox_colors = {'Low Toxicity': '#27ae60', 'High Toxicity': '#e74c3c'}
for tox, color in tox_colors.items():
    mask = df_gxe['risk_category'] == tox
    ax3.scatter(pca_gxe_result[mask, 0], pca_gxe_result[mask, 1], 
                c=color, label=tox, alpha=0.5, s=20)
ax3.set_xlabel(f'PC1 ({pca_gxe.explained_variance_ratio_[0]*100:.1f}%)')
ax3.set_ylabel(f'PC2 ({pca_gxe.explained_variance_ratio_[1]*100:.1f}%)')
ax3.set_title('C: By Toxicity Outcome', fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: 3D PCA projection
ax4 = axes[1, 1]
pca_3d = PCA(n_components=3)
pca_result_3d = pca_3d.fit_transform(X_gxe_scaled)
scatter = ax4.scatter(pca_result_3d[:, 0], pca_result_3d[:, 1], 
                      c=df_gxe['toxicity'], cmap='RdYlGn_r', alpha=0.5, s=20)
ax4.set_xlabel(f'PC1 ({pca_3d.explained_variance_ratio_[0]*100:.1f}%)')
ax4.set_ylabel(f'PC2 ({pca_3d.explained_variance_ratio_[1]*100:.1f}%)')
ax4.set_title('D: Toxicity Risk (Color Scale)', fontweight='bold')
plt.colorbar(scatter, ax=ax4, label='Toxicity Probability')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_gxe_interaction.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/pca_gxe_interaction.pdf', bbox_inches='tight')
print("  ✓ Saved: pca_gxe_interaction.png/pdf")

# ============================================================
# 5. VARIANCE EXPLAINED BAR PLOT
# ============================================================
print("\n[5/6] Creating Variance Explained Plot...")

# PCA on full dataset
features_full = ['genetic_risk', 'ses_risk', 'equity_score', 'genotype', 'toxicity']
X_full = df_gxe[['genotype', 'ses_score', 'toxicity']].copy()
X_full['genetic_risk'] = df_equity['genetic_risk'].iloc[:len(X_full)]
X_full['ses_risk'] = df_equity['ses_risk'].iloc[:len(X_full)]
X_full['equity_score'] = df_equity['equity_score'].iloc[:len(X_full)]

scaler_full = StandardScaler()
X_full_scaled = scaler_full.fit_transform(X_full)
pca_full = PCA()
pca_full.fit(X_full_scaled)

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))

components = range(1, len(pca_full.explained_variance_ratio_) + 1)
bars = ax.bar(components, pca_full.explained_variance_ratio_ * 100, alpha=0.7, 
              color='steelblue', edgecolor='black')
ax.plot(components, np.cumsum(pca_full.explained_variance_ratio_) * 100, 
        'ro-', linewidth=2, markersize=8, label='Cumulative variance')

ax.set_xlabel('Principal Component', fontsize=12)
ax.set_ylabel('Variance Explained (%)', fontsize=12)
ax.set_title('PCA Variance Explained - Full Feature Set', fontsize=14, fontweight='bold')
ax.set_xticks(components)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, (bar, var) in enumerate(zip(bars, pca_full.explained_variance_ratio_ * 100)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
            f'{var:.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_variance_explained.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/pca_variance_explained.pdf', bbox_inches='tight')
print("  ✓ Saved: pca_variance_explained.png/pdf")

# ============================================================
# 6. 3D PCA PLOT (Interactive)
# ============================================================
print("\n[6/6] Creating 3D PCA Plot...")

from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Use first 3 PCs
pca_3d_full = PCA(n_components=3)
pca_3d_result = pca_3d_full.fit_transform(X_full_scaled)

# Color by risk category
risk_categories = df_equity['risk_category'].iloc[:len(pca_3d_result)]
risk_colors_3d = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
                  'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}

for risk, color in risk_colors_3d.items():
    mask = risk_categories == risk
    ax.scatter(pca_3d_result[mask, 0], pca_3d_result[mask, 1], pca_3d_result[mask, 2],
               c=color, label=risk, alpha=0.6, s=30)

ax.set_xlabel(f'PC1 ({pca_3d_full.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
ax.set_ylabel(f'PC2 ({pca_3d_full.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
ax.set_zlabel(f'PC3 ({pca_3d_full.explained_variance_ratio_[2]*100:.1f}%)', fontsize=11)
ax.set_title('3D PCA: Risk Components by Category', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_3d.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/pca_3d.pdf', bbox_inches='tight')
print("  ✓ Saved: pca_3d.png/pdf")

# ============================================================
# 7. SUMMARY REPORT
# ============================================================
print("\n" + "="*60)
print("PCA ANALYSIS COMPLETE!")
print("="*60)

print("\n📊 Generated Files:")
print("  • data/processed/figures/pca_genetic_ancestry.png/pdf")
print("  • data/processed/figures/pca_ses_equity.png/pdf")
print("  • data/processed/figures/pca_gxe_interaction.png/pdf")
print("  • data/processed/figures/pca_variance_explained.png/pdf")
print("  • data/processed/figures/pca_3d.png/pdf")

print("\n📈 Variance Explained Summary:")
for i, var in enumerate(pca_full.explained_variance_ratio_[:5], 1):
    print(f"  PC{i}: {var*100:.1f}%")
print(f"  Total (first 5 PCs): {pca_full.explained_variance_ratio_[:5].sum()*100:.1f}%")

print("\n✅ All PCA visualizations saved to data/processed/figures/")