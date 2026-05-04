# umap_complete_analysis.py
# UMAP Analysis for Pharmacogenomic Equity Atlas
# Better than PCA for genetic data - preserves local structure

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("UMAP ANALYSIS FOR PHARMACOGENOMIC EQUITY ATLAS")
print("="*60)

# Install umap if not already installed
try:
    import umap
    print("✓ UMAP already installed")
except ImportError:
    print("Installing UMAP...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'umap-learn'])
    import umap

# Create output directory
import os
os.makedirs('data/processed/figures', exist_ok=True)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("\n[1/6] Loading data...")

# Load equity scores
df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded {len(df):,} patient records")

# ============================================================
# 2. PREPARE FEATURES FOR UMAP
# ============================================================
print("\n[2/6] Preparing features for UMAP...")

# Select features for UMAP
feature_cols = ['genetic_risk', 'ses_risk', 'equity_score']

# Add ancestry as numeric
ancestry_map = {'AFR': 0, 'EUR': 1, 'EAS': 2, 'SAS': 3, 'AMR': 4}
df['ancestry_numeric'] = df['ancestry'].map(ancestry_map)

# Add risk category numeric
risk_map = {'Low Risk': 0, 'Moderate Risk': 1, 'High Risk': 2, 'Very High Risk': 3}
df['risk_numeric'] = df['risk_category'].map(risk_map)

# Full feature set
all_features = feature_cols + ['ancestry_numeric', 'risk_numeric']
X = df[all_features].dropna().values

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"  ✓ Features: {len(all_features)} dimensions")
print(f"  ✓ Samples: {len(X_scaled):,}")

# ============================================================
# 3. RUN UMAP WITH DIFFERENT PARAMETERS
# ============================================================
print("\n[3/6] Running UMAP with optimized parameters...")

# UMAP parameters
umap_params = {
    'n_neighbors': 15,      # Local neighborhood size (10-30 is good)
    'min_dist': 0.1,        # Minimum distance between points (0.1-0.5)
    'n_components': 2,      # 2D projection
    'metric': 'euclidean',  # Distance metric
    'random_state': 42
}

print(f"  Parameters: n_neighbors={umap_params['n_neighbors']}, min_dist={umap_params['min_dist']}")

# Run UMAP
reducer = umap.UMAP(**umap_params)
umap_result = reducer.fit_transform(X_scaled)

print(f"  ✓ UMAP completed - shape: {umap_result.shape}")

# ============================================================
# 4. CREATE UMAP VISUALIZATIONS
# ============================================================
print("\n[4/6] Creating UMAP visualizations...")

# Get valid indices (after dropping NA)
valid_indices = df[all_features].dropna().index
df_umap = df.loc[valid_indices].copy()
df_umap['UMAP1'] = umap_result[:, 0]
df_umap['UMAP2'] = umap_result[:, 1]

# Figure 1: UMAP colored by Ancestry
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('UMAP Analysis of Pharmacogenomic Risk Factors', fontsize=16, fontweight='bold')

# Plot 1: By Ancestry
ax1 = axes[0, 0]
colors_ancestry = {'AFR': '#e41a1c', 'EUR': '#377eb8', 'EAS': '#4daf4a', 
                   'SAS': '#984ea3', 'AMR': '#ff7f00'}
for ancestry in df_umap['ancestry'].unique():
    mask = df_umap['ancestry'] == ancestry
    ax1.scatter(df_umap.loc[mask, 'UMAP1'], df_umap.loc[mask, 'UMAP2'],
                c=colors_ancestry[ancestry], label=ancestry, alpha=0.5, s=15, edgecolors='white', linewidth=0.3)
ax1.set_xlabel('UMAP Dimension 1', fontsize=11)
ax1.set_ylabel('UMAP Dimension 2', fontsize=11)
ax1.set_title('A: Colored by Ancestry', fontweight='bold')
ax1.legend(loc='best', fontsize=9)
ax1.grid(True, alpha=0.2)

# Plot 2: By Risk Category
ax2 = axes[0, 1]
risk_colors = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
               'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}
for risk, color in risk_colors.items():
    mask = df_umap['risk_category'] == risk
    ax2.scatter(df_umap.loc[mask, 'UMAP1'], df_umap.loc[mask, 'UMAP2'],
                c=color, label=risk, alpha=0.5, s=15, edgecolors='white', linewidth=0.3)
ax2.set_xlabel('UMAP Dimension 1', fontsize=11)
ax2.set_ylabel('UMAP Dimension 2', fontsize=11)
ax2.set_title('B: Colored by Risk Category', fontweight='bold')
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.2)

# Plot 3: By Equity Score (continuous color)
ax3 = axes[1, 0]
scatter3 = ax3.scatter(df_umap['UMAP1'], df_umap['UMAP2'],
                       c=df_umap['equity_score'], cmap='RdYlGn_r', 
                       alpha=0.5, s=15, edgecolors='white', linewidth=0.3)
ax3.set_xlabel('UMAP Dimension 1', fontsize=11)
ax3.set_ylabel('UMAP Dimension 2', fontsize=11)
ax3.set_title('C: Colored by Equity Score', fontweight='bold')
cbar3 = plt.colorbar(scatter3, ax=ax3)
cbar3.set_label('Equity Score', fontsize=10)
ax3.grid(True, alpha=0.2)

# Plot 4: By Genetic Risk
ax4 = axes[1, 1]
scatter4 = ax4.scatter(df_umap['UMAP1'], df_umap['UMAP2'],
                       c=df_umap['genetic_risk'], cmap='viridis', 
                       alpha=0.5, s=15, edgecolors='white', linewidth=0.3)
ax4.set_xlabel('UMAP Dimension 1', fontsize=11)
ax4.set_ylabel('UMAP Dimension 2', fontsize=11)
ax4.set_title('D: Colored by Genetic Risk', fontweight='bold')
cbar4 = plt.colorbar(scatter4, ax=ax4)
cbar4.set_label('Genetic Risk Score', fontsize=10)
ax4.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_full_analysis.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/umap_full_analysis.pdf', bbox_inches='tight')
print("  ✓ Saved: umap_full_analysis.png/pdf")

# ============================================================
# 5. PARAMETER SWEEP (Finding optimal UMAP settings)
# ============================================================
print("\n[5/6] Testing different UMAP parameters...")

param_combinations = [
    {'n_neighbors': 5, 'min_dist': 0.05, 'name': 'Tight Clusters'},
    {'n_neighbors': 15, 'min_dist': 0.1, 'name': 'Balanced'},
    {'n_neighbors': 30, 'min_dist': 0.3, 'name': 'Loose Clusters'},
    {'n_neighbors': 50, 'min_dist': 0.5, 'name': 'Global Structure'},
]

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('UMAP Parameter Optimization - n_neighbors vs min_dist', fontsize=14, fontweight='bold')

for idx, params in enumerate(param_combinations):
    row, col = divmod(idx, 2)
    ax = axes[row, col]
    
    # Run UMAP with different parameters
    reducer_test = umap.UMAP(n_neighbors=params['n_neighbors'], 
                              min_dist=params['min_dist'],
                              n_components=2, random_state=42)
    result_test = reducer_test.fit_transform(X_scaled)
    
    scatter = ax.scatter(result_test[:, 0], result_test[:, 1],
                         c=df_umap['equity_score'], cmap='RdYlGn_r', 
                         alpha=0.5, s=10)
    ax.set_xlabel('UMAP1', fontsize=10)
    ax.set_ylabel('UMAP2', fontsize=10)
    ax.set_title(f"{params['name']}: n={params['n_neighbors']}, d={params['min_dist']}", fontsize=10)
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_parameter_sweep.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: umap_parameter_sweep.png")

# ============================================================
# 6. 3D UMAP
# ============================================================
print("\n[6/6] Creating 3D UMAP visualization...")

# Run 3D UMAP
reducer_3d = umap.UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=42)
umap_3d_result = reducer_3d.fit_transform(X_scaled)

# Create 3D plot
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Color by risk category
risk_colors_3d = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
                  'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}

for risk, color in risk_colors_3d.items():
    mask = df_umap['risk_category'] == risk
    ax.scatter(umap_3d_result[mask, 0], umap_3d_result[mask, 1], umap_3d_result[mask, 2],
               c=color, label=risk, alpha=0.4, s=15)

ax.set_xlabel('UMAP Dimension 1', fontsize=12)
ax.set_ylabel('UMAP Dimension 2', fontsize=12)
ax.set_zlabel('UMAP Dimension 3', fontsize=12)
ax.set_title('3D UMAP Projection - Risk Categories', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)

plt.tight_layout()
plt.savefig('data/processed/figures/umap_3d.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/umap_3d.pdf', bbox_inches='tight')
print("  ✓ Saved: umap_3d.png/pdf")

# ============================================================
# 7. PCA vs UMAP COMPARISON
# ============================================================
print("\n[7/7] Creating PCA vs UMAP comparison...")

# Run PCA for comparison
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# PCA
ax1 = axes[0]
for ancestry in df_umap['ancestry'].unique():
    mask = df_umap['ancestry'] == ancestry
    ax1.scatter(pca_result[mask, 0], pca_result[mask, 1],
                c=colors_ancestry[ancestry], label=ancestry, alpha=0.5, s=15)
ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
ax1.set_title('PCA - Linear Projection', fontweight='bold')
ax1.legend(loc='best', fontsize=9)
ax1.grid(True, alpha=0.2)

# UMAP
ax2 = axes[1]
for ancestry in df_umap['ancestry'].unique():
    mask = df_umap['ancestry'] == ancestry
    ax2.scatter(df_umap.loc[mask, 'UMAP1'], df_umap.loc[mask, 'UMAP2'],
                c=colors_ancestry[ancestry], label=ancestry, alpha=0.5, s=15)
ax2.set_xlabel('UMAP Dimension 1')
ax2.set_ylabel('UMAP Dimension 2')
ax2.set_title('UMAP - Non-linear Manifold Learning', fontweight='bold')
ax2.legend(loc='best', fontsize=9)
ax2.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_vs_umap.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: pca_vs_umap.png")

# ============================================================
# 8. SUMMARY STATISTICS
# ============================================================
print("\n" + "="*60)
print("UMAP ANALYSIS COMPLETE!")
print("="*60)

print("\n📊 Generated UMAP Files:")
print("  • umap_full_analysis.png/pdf - 4-panel comprehensive view")
print("  • umap_parameter_sweep.png - Parameter optimization")
print("  • umap_3d.png/pdf - 3D projection")
print("  • pca_vs_umap.png - Comparison with PCA")

print("\n📈 UMAP Interpretation:")
print("  • UMAP preserves local structure better than PCA")
print("  • Clusters represent similar risk profiles")
print("  • Distance between groups indicates dissimilarity")
print("  • Non-linear relationships captured effectively")

# Save UMAP coordinates for web app
df_umap[['individual_id', 'ancestry', 'risk_category', 'equity_score', 
         'genetic_risk', 'ses_risk', 'UMAP1', 'UMAP2']].to_csv(
    'data/processed/umap_coordinates.csv', index=False)
print("\n  ✓ Saved UMAP coordinates for web app integration")
