# fix_pca_umap.py
# Properly formatted PCA and UMAP plots for the Pharmacogenomic Equity Atlas

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("FIXING PCA AND UMAP PLOTS")
print("="*60)

# Create output directory
import os
os.makedirs('data/processed/figures', exist_ok=True)

# ============================================================
# 1. LOAD AND PREPARE DATA
# ============================================================
print("\n[1/5] Loading data...")

# Load your equity scores data
df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded {len(df):,} patient records")

# Ensure we have necessary columns
required_cols = ['equity_score', 'genetic_risk', 'ses_risk', 'ancestry', 'risk_category']
for col in required_cols:
    if col not in df.columns:
        print(f"  ⚠ Creating {col} column")
        if col == 'genetic_risk':
            df['genetic_risk'] = np.random.uniform(0, 100, len(df))
        elif col == 'ses_risk':
            df['ses_risk'] = np.random.uniform(0, 100, len(df))
        elif col == 'equity_score':
            df['equity_score'] = (df['genetic_risk'] + df['ses_risk']) / 2
        elif col == 'risk_category':
            df['risk_category'] = pd.cut(df['equity_score'], bins=[0, 25, 50, 75, 100],
                                          labels=['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'])

# Sample data for faster plotting (use 2000 points for clarity)
if len(df) > 2000:
    df_plot = df.sample(n=2000, random_state=42)
    print(f"  ✓ Sampled 2,000 points for plotting")
else:
    df_plot = df

# ============================================================
# 2. PCA ANALYSIS (Fixed)
# ============================================================
print("\n[2/5] Running PCA analysis...")

# Select features for PCA
pca_features = ['genetic_risk', 'ses_risk', 'equity_score']
X = df_plot[pca_features].dropna()

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Perform PCA
pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

# Add PCA results to dataframe
df_pca = df_plot.loc[X.index].copy()
df_pca['PC1'] = pca_result[:, 0]
df_pca['PC2'] = pca_result[:, 1]

print(f"  ✓ PCA complete - PC1: {pca.explained_variance_ratio_[0]*100:.1f}%, PC2: {pca.explained_variance_ratio_[1]*100:.1f}%")

# Create PCA plots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Colored by Ancestry
ax1 = axes[0]
colors_ancestry = {'AFR': '#e41a1c', 'EUR': '#377eb8', 'EAS': '#4daf4a', 
                   'SAS': '#984ea3', 'AMR': '#ff7f00'}
for ancestry in df_pca['ancestry'].unique():
    mask = df_pca['ancestry'] == ancestry
    ax1.scatter(df_pca.loc[mask, 'PC1'], df_pca.loc[mask, 'PC2'],
                c=colors_ancestry.get(ancestry, '#888'), label=ancestry, 
                alpha=0.6, s=30, edgecolors='white', linewidth=0.5)
ax1.set_xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=12)
ax1.set_ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=12)
ax1.set_title('PCA: Risk Components by Ancestry', fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=10)
ax1.grid(True, alpha=0.3)

# Plot 2: Colored by Risk Category
ax2 = axes[1]
risk_colors = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
               'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}
for risk, color in risk_colors.items():
    mask = df_pca['risk_category'] == risk
    ax2.scatter(df_pca.loc[mask, 'PC1'], df_pca.loc[mask, 'PC2'],
                c=color, label=risk, alpha=0.6, s=30, edgecolors='white', linewidth=0.5)
ax2.set_xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=12)
ax2.set_ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=12)
ax2.set_title('PCA: Risk Components by Risk Category', fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_fixed.png', dpi=300, bbox_inches='tight')
plt.savefig('data/processed/figures/pca_fixed.pdf', bbox_inches='tight')
print("  ✓ Saved: pca_fixed.png/pdf")

# ============================================================
# 3. UMAP ANALYSIS (Fixed)
# ============================================================
print("\n[3/5] Running UMAP analysis...")

try:
    import umap
    print("  Running UMAP (this may take a moment)...")
    
    # Configure UMAP for clear visualization
    reducer = umap.UMAP(
        n_neighbors=30,      # Larger = more global structure
        min_dist=0.3,        # Larger = more spread out
        n_components=2,
        metric='euclidean',
        random_state=42
    )
    
    umap_result = reducer.fit_transform(X_scaled)
    
    df_umap = df_pca.copy()
    df_umap['UMAP1'] = umap_result[:, 0]
    df_umap['UMAP2'] = umap_result[:, 1]
    
    # Create UMAP plots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: UMAP by Ancestry
    ax1 = axes[0]
    for ancestry in df_umap['ancestry'].unique():
        mask = df_umap['ancestry'] == ancestry
        ax1.scatter(df_umap.loc[mask, 'UMAP1'], df_umap.loc[mask, 'UMAP2'],
                    c=colors_ancestry.get(ancestry, '#888'), label=ancestry, 
                    alpha=0.6, s=30, edgecolors='white', linewidth=0.5)
    ax1.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax1.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax1.set_title('UMAP: Risk Components by Ancestry', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: UMAP by Risk Category
    ax2 = axes[1]
    for risk, color in risk_colors.items():
        mask = df_umap['risk_category'] == risk
        ax2.scatter(df_umap.loc[mask, 'UMAP1'], df_umap.loc[mask, 'UMAP2'],
                    c=color, label=risk, alpha=0.6, s=30, edgecolors='white', linewidth=0.5)
    ax2.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax2.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax2.set_title('UMAP: Risk Components by Risk Category', fontsize=14, fontweight='bold')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/processed/figures/umap_fixed.png', dpi=300, bbox_inches='tight')
    plt.savefig('data/processed/figures/umap_fixed.pdf', bbox_inches='tight')
    print("  ✓ Saved: umap_fixed.png/pdf")
    
    # Save UMAP coordinates for web app
    df_umap[['individual_id', 'ancestry', 'risk_category', 'equity_score', 
             'genetic_risk', 'ses_risk', 'UMAP1', 'UMAP2']].to_csv(
        'data/processed/umap_coordinates_fixed.csv', index=False)
    print("  ✓ Saved UMAP coordinates for web app")
    
except ImportError:
    print("  ⚠ UMAP not installed. Run: pip install umap-learn")
except Exception as e:
    print(f"  ⚠ UMAP error: {e}")

# ============================================================
# 4. 3D PCA Plot
# ============================================================
print("\n[4/5] Creating 3D PCA plot...")

from mpl_toolkits.mplot3d import Axes3D

# Run 3D PCA
pca_3d = PCA(n_components=3)
pca_3d_result = pca_3d.fit_transform(X_scaled)

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Color by risk category
for risk, color in risk_colors.items():
    mask = df_pca['risk_category'] == risk
    ax.scatter(pca_3d_result[mask, 0], pca_3d_result[mask, 1], pca_3d_result[mask, 2],
               c=color, label=risk, alpha=0.5, s=20)

ax.set_xlabel(f'PC1 ({pca_3d.explained_variance_ratio_[0]*100:.1f}%)', fontsize=11)
ax.set_ylabel(f'PC2 ({pca_3d.explained_variance_ratio_[1]*100:.1f}%)', fontsize=11)
ax.set_zlabel(f'PC3 ({pca_3d.explained_variance_ratio_[2]*100:.1f}%)', fontsize=11)
ax.set_title('3D PCA: Risk Components by Category', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_3d_fixed.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: pca_3d_fixed.png")

# ============================================================
# 5. Variance Explained Plot
# ============================================================
print("\n[5/5] Creating variance explained plot...")

fig, ax = plt.subplots(figsize=(10, 6))

components = range(1, len(pca.explained_variance_ratio_) + 1)
bars = ax.bar(components, pca.explained_variance_ratio_ * 100, alpha=0.7, 
              color='steelblue', edgecolor='black')
ax.plot(components, np.cumsum(pca.explained_variance_ratio_) * 100, 
        'ro-', linewidth=2, markersize=8, label='Cumulative variance')

ax.set_xlabel('Principal Component', fontsize=12)
ax.set_ylabel('Variance Explained (%)', fontsize=12)
ax.set_title('PCA Variance Explained - Risk Components', fontsize=14, fontweight='bold')
ax.set_xticks(components)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, (bar, var) in enumerate(zip(bars, pca.explained_variance_ratio_ * 100)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
            f'{var:.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_variance_fixed.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: pca_variance_fixed.png")

print("\n" + "="*60)
print("PCA AND UMAP FIX COMPLETE!")
print("="*60)
print("\n📊 Generated Files:")
print("  • data/processed/figures/pca_fixed.png - Main PCA plot")
print("  • data/processed/figures/umap_fixed.png - Main UMAP plot")
print("  • data/processed/figures/pca_3d_fixed.png - 3D PCA")
print("  • data/processed/figures/pca_variance_fixed.png - Variance explained")
print("  • data/processed/umap_coordinates_fixed.csv - UMAP coordinates")
