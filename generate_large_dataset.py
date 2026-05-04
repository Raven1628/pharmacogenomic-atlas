# generate_large_dataset.py
# Generate larger dataset for better PCA and power

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

print("="*60)
print("GENERATING LARGER DATASET")
print("="*60)

# Parameters
n_samples = 50000  # Increased from 5000
n_variants = 100   # Increased from 10
n_drugs = 20       # Increased from 10

print(f"\nGenerating {n_samples:,} samples with {n_variants} variants...")

np.random.seed(42)

# Generate ancestry (more fine-grained)
ancestries = np.random.choice(
    ['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], 
    n_samples, 
    p=[0.26, 0.20, 0.20, 0.20, 0.14]
)

# Generate SES scores (continuous)
ses_scores = np.zeros(n_samples)
for i, ancestry in enumerate(ancestries):
    if ancestry in ['AFR', 'AMR']:
        ses_scores[i] = np.random.beta(3, 2)  # Higher vulnerability
    elif ancestry == 'SAS':
        ses_scores[i] = np.random.beta(2.5, 2.5)
    else:
        ses_scores[i] = np.random.beta(2, 3)  # Lower vulnerability

# Generate genotypes (more variants)
genotypes = np.random.choice([0, 1, 2], (n_samples, n_variants), p=[0.6, 0.35, 0.05])

# Calculate genetic risk (weighted sum)
genetic_risk = genotypes.sum(axis=1) * (100 / (n_variants * 2))

# Calculate equity score
equity_score = genetic_risk * 0.5 + ses_scores * 50

# Determine risk category
risk_categories = np.where(equity_score < 25, 'Low Risk',
                  np.where(equity_score < 50, 'Moderate Risk',
                  np.where(equity_score < 75, 'High Risk', 'Very High Risk')))

# Create DataFrame
df_large = pd.DataFrame({
    'individual_id': [f"IND_{i:06d}" for i in range(n_samples)],
    'ancestry': ancestries,
    'ses_score': ses_scores,
    'genetic_risk': genetic_risk,
    'equity_score': equity_score,
    'risk_category': risk_categories
})

# Add genotype columns
for i in range(n_variants):
    df_large[f'variant_{i}'] = genotypes[:, i]

# Save
df_large.to_csv('data/processed/large_dataset.csv', index=False)
print(f"✓ Saved {len(df_large):,} samples to large_dataset.csv")

# PCA on larger dataset
print("\nRunning PCA on larger dataset...")
features = ['genetic_risk', 'ses_score', 'equity_score']
X = df_large[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

# Create improved PCA plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# By ancestry
ax1 = axes[0]
colors = {'AFR': '#e41a1c', 'EUR': '#377eb8', 'EAS': '#4daf4a', 
          'SAS': '#984ea3', 'AMR': '#ff7f00'}
for ancestry in df_large['ancestry'].unique():
    mask = df_large['ancestry'] == ancestry
    ax1.scatter(pca_result[mask, 0], pca_result[mask, 1], 
                c=colors[ancestry], label=ancestry, alpha=0.3, s=10)
ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
ax1.set_title(f'PCA: {n_samples:,} Samples, {n_variants} Variants')
ax1.legend()
ax1.grid(True, alpha=0.3)

# By risk category
ax2 = axes[1]
risk_colors = {'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
               'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'}
for risk, color in risk_colors.items():
    mask = df_large['risk_category'] == risk
    ax2.scatter(pca_result[mask, 0], pca_result[mask, 1], 
                c=color, label=risk, alpha=0.3, s=10)
ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
ax2.set_title('Risk Categories')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/processed/figures/pca_large_dataset.png', dpi=300)
print("✓ Saved: pca_large_dataset.png")

print("\n" + "="*60)
print("LARGE DATASET GENERATION COMPLETE!")
print(f"Sample size: {n_samples:,}")
print(f"Variants: {n_variants}")
print(f"Variance explained: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, PC2={pca.explained_variance_ratio_[1]*100:.1f}%")
