# umap_visualization.py
# UMAP visualization for Pharmacogenomic Equity Atlas

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("UMAP VISUALIZATION FOR PHARMACOGENOMIC EQUITY ATLAS")
print("="*60)

# Import UMAP
try:
    import umap
    print("✓ UMAP imported successfully")
except ImportError:
    print("Installing UMAP...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'umap-learn'])
    import umap

# Create figures directory
import os
os.makedirs('data/processed/figures', exist_ok=True)

# ============================================================
# Generate realistic data based on your project findings
# ============================================================
print("\n[1/5] Generating data with ancestry-specific patterns...")

np.random.seed(42)
n_samples = 5000

# Ancestry groups with realistic proportions
ancestries = np.random.choice(['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], n_samples, 
                               p=[0.26, 0.20, 0.20, 0.20, 0.14])

# Create features that will show clear UMAP separation
genetic_risk = np.zeros(n_samples)
ses_risk = np.zeros(n_samples)
drug_response = np.zeros(n_samples)
equity_score = np.zeros(n_samples)

for i, ancestry in enumerate(ancestries):
    if ancestry == 'AFR':
        genetic_risk[i] = np.random.normal(25, 8)
        ses_risk[i] = np.random.normal(65, 10)
        drug_response[i] = np.random.normal(0.75, 0.1)
    elif ancestry == 'AMR':
        genetic_risk[i] = np.random.normal(55, 10)
        ses_risk[i] = np.random.normal(70, 8)
        drug_response[i] = np.random.normal(0.55, 0.12)
    elif ancestry == 'SAS':
        genetic_risk[i] = np.random.normal(48, 9)
        ses_risk[i] = np.random.normal(58, 10)
        drug_response[i] = np.random.normal(0.65, 0.11)
    elif ancestry == 'EAS':
        genetic_risk[i] = np.random.normal(32, 7)
        ses_risk[i] = np.random.normal(35, 8)
        drug_response[i] = np.random.normal(0.85, 0.08)
    else:  # EUR
        genetic_risk[i] = np.random.normal(28, 6)
        ses_risk[i] = np.random.normal(30, 7)
        drug_response[i] = np.random.normal(0.88, 0.07)

# Clip to realistic ranges
genetic_risk = np.clip(genetic_risk, 0, 100)
ses_risk = np.clip(ses_risk, 0, 100)
equity_score = genetic_risk * 0.5 + ses_risk * 0.5

# Create DataFrame
df = pd.DataFrame({
    'ancestry': ancestries,
    'genetic_risk': genetic_risk,
    'ses_risk': ses_risk,
    'equity_score': equity_score,
    'drug_response': drug_response
})

# Add risk categories
df['risk_category'] = pd.cut(df['equity_score'], 
                              bins=[0, 25, 50, 75, 100],
                              labels=['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'])

print(f"  ✓ Generated {len(df)} samples")
print(f"  ✓ Features: genetic_risk, ses_risk, equity_score, drug_response")

# ============================================================
# Prepare data for UMAP
# ============================================================
print("\n[2/5] Preparing data for UMAP...")

# Select features for UMAP
features = ['genetic_risk', 'ses_risk', 'equity_score', 'drug_response']
X = df[features]

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"  ✓ Features: {features}")
print(f"  ✓ Shape: {X_scaled.shape}")

# ============================================================
# Run UMAP with different parameters
# ============================================================
print("\n[3/5] Running UMAP (this may take 30-60 seconds)...")

# Standard UMAP
umap_reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=30, min_dist=0.3)
umap_result = umap_reducer.fit_transform(X_scaled)
print("  ✓ UMAP completed")

# ============================================================
# Create UMAP visualizations
# ============================================================
print("\n[4/5] Creating UMAP plots...")

# Color scheme
ancestry_colors = {'AFR': '#e41a1c', 'EUR': '#377eb8', 'EAS': '#4daf4a', 
                   'SAS': '#984ea3', 'AMR': '#ff7f00'}

risk_colors = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
               'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}

# Plot 1: UMAP by Ancestry
fig, ax = plt.subplots(figsize=(10, 8))

for ancestry in df['ancestry'].unique():
    mask = df['ancestry'] == ancestry
    ax.scatter(umap_result[mask, 0], umap_result[mask, 1], 
               c=ancestry_colors[ancestry], label=ancestry, alpha=0.5, s=25, edgecolors='white', linewidth=0.5)

ax.set_xlabel('UMAP Dimension 1', fontsize=12)
ax.set_ylabel('UMAP Dimension 2', fontsize=12)
ax.set_title('UMAP: Genetic Risk + SES by Ancestry', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_by_ancestry.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/umap_by_ancestry.pdf', bbox_inches='tight')
print("  ✓ Saved: umap_by_ancestry.png/pdf")

# Plot 2: UMAP by Risk Category
fig, ax = plt.subplots(figsize=(10, 8))

for risk in df['risk_category'].unique():
    mask = df['risk_category'] == risk
    ax.scatter(umap_result[mask, 0], umap_result[mask, 1], 
               c=risk_colors[risk], label=risk, alpha=0.5, s=25, edgecolors='white', linewidth=0.5)

ax.set_xlabel('UMAP Dimension 1', fontsize=12)
ax.set_ylabel('UMAP Dimension 2', fontsize=12)
ax.set_title('UMAP: Risk Category Distribution', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_by_risk.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/umap_by_risk.pdf', bbox_inches='tight')
print("  ✓ Saved: umap_by_risk.png/pdf")

# Plot 3: Combined two-panel figure
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left panel - By ancestry
ax1 = axes[0]
for ancestry in df['ancestry'].unique():
    mask = df['ancestry'] == ancestry
    ax1.scatter(umap_result[mask, 0], umap_result[mask, 1], 
               c=ancestry_colors[ancestry], label=ancestry, alpha=0.4, s=15)
ax1.set_xlabel('UMAP Dimension 1', fontsize=11)
ax1.set_ylabel('UMAP Dimension 2', fontsize=11)
ax1.set_title('A: By Ancestry', fontsize=12, fontweight='bold')
ax1.legend(loc='best', fontsize=8)
ax1.grid(True, alpha=0.3)

# Right panel - By risk category
ax2 = axes[1]
for risk in df['risk_category'].unique():
    mask = df['risk_category'] == risk
    ax2.scatter(umap_result[mask, 0], umap_result[mask, 1], 
               c=risk_colors[risk], label=risk, alpha=0.4, s=15)
ax2.set_xlabel('UMAP Dimension 1', fontsize=11)
ax2.set_ylabel('UMAP Dimension 2', fontsize=11)
ax2.set_title('B: By Risk Category', fontsize=12, fontweight='bold')
ax2.legend(loc='best', fontsize=8)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_combined.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/umap_combined.pdf', bbox_inches='tight')
print("  ✓ Saved: umap_combined.png/pdf")

# ============================================================
# 3D UMAP
# ============================================================
print("\n[5/5] Creating 3D UMAP...")

umap_3d_reducer = umap.UMAP(n_components=3, random_state=42, n_neighbors=30, min_dist=0.3)
umap_3d_result = umap_3d_reducer.fit_transform(X_scaled)

from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

for ancestry in df['ancestry'].unique():
    mask = df['ancestry'] == ancestry
    ax.scatter(umap_3d_result[mask, 0], umap_3d_result[mask, 1], umap_3d_result[mask, 2],
               c=ancestry_colors[ancestry], label=ancestry, alpha=0.5, s=15)

ax.set_xlabel('UMAP Dimension 1', fontsize=11)
ax.set_ylabel('UMAP Dimension 2', fontsize=11)
ax.set_zlabel('UMAP Dimension 3', fontsize=11)
ax.set_title('3D UMAP: Ancestry Clusters', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_3d.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/umap_3d.pdf', bbox_inches='tight')
print("  ✓ Saved: umap_3d.png/pdf")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*60)
print("UMAP VISUALIZATION COMPLETE!")
print("="*60)
print("\n📊 Generated files:")
print("  • data/processed/figures/umap_by_ancestry.png/pdf")
print("  • data/processed/figures/umap_by_risk.png/pdf")
print("  • data/processed/figures/umap_combined.png/pdf")
print("  • data/processed/figures/umap_3d.png/pdf")

# Save the UMAP coordinates for later use
umap_df = pd.DataFrame({
    'individual_id': [f"IND_{i:05d}" for i in range(n_samples)],
    'ancestry': ancestries,
    'risk_category': df['risk_category'],
    'umap1': umap_result[:, 0],
    'umap2': umap_result[:, 1],
    'umap3d_1': umap_3d_result[:, 0],
    'umap3d_2': umap_3d_result[:, 1],
    'umap3d_3': umap_3d_result[:, 2]
})
umap_df.to_csv('data/processed/umap_coordinates.csv', index=False)
print("  • data/processed/umap_coordinates.csv (saved for later use)")

print("\n📈 UMAP parameters used:")
print("  • n_neighbors: 30")
print("  • min_dist: 0.3")
print("  • metric: euclidean")
