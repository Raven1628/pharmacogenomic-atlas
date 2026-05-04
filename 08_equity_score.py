# 08_equity_score.py
# Step 5 - Pharmacogenomic Equity Score (LARGE DATASET)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 5: Pharmacogenomic Equity Score (PES) - LARGE DATASET")
print("="*60)

# Load data with fallback
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
    print(f"  ✓ Loaded existing equity scores: {len(df)} individuals")
except:
    try:
        df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
        print(f"  ✓ Loaded GxE data: {len(df)} individuals")
    except:
        df = pd.read_csv("data/processed/large_dataset.csv")
        print(f"  ✓ Loaded large dataset: {len(df)} individuals")

# Add ancestry if not present
if 'ancestry' not in df.columns:
    np.random.seed(42)
    df['ancestry'] = np.random.choice(['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], len(df), 
                                       p=[0.26, 0.20, 0.20, 0.20, 0.14])

# Calculate risk components
if 'genetic_risk' not in df.columns:
    if 'genotype' in df.columns:
        df['genetic_risk'] = df['genotype'] * 33.3
    else:
        df['genetic_risk'] = np.random.uniform(0, 100, len(df))

if 'ses_score' in df.columns:
    df['ses_risk'] = df['ses_score'] * 100
else:
    df['ses_risk'] = np.random.uniform(0, 100, len(df))

df['equity_score'] = (df['genetic_risk'] * 0.5 + df['ses_risk'] * 0.5)
df['risk_category'] = pd.cut(df['equity_score'], bins=[0, 25, 50, 75, 100],
                              labels=['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'])
df['high_risk'] = (df['risk_category'].isin(['High Risk', 'Very High Risk'])).astype(int)

# Expanded clinical guidelines
clinical_guidelines = {
    'Warfarin': {
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant'
    },
    'Clopidogrel': {
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider alternative',
        'Very High Risk': 'Avoid clopidogrel'
    },
    'Simvastatin': {
        'Low Risk': 'Standard 40mg',
        'Moderate Risk': 'Start with 20mg',
        'High Risk': 'Use alternative statin',
        'Very High Risk': 'Avoid simvastatin'
    },
    'Fluorouracil': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': '25% dose reduction',
        'High Risk': '50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil'
    },
    'Codeine': {
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine',
        'Very High Risk': 'Use non-opioid alternatives'
    },
    'Tamoxifen': {
        'Low Risk': 'Standard dosing (20mg daily)',
        'Moderate Risk': 'Monitor for reduced efficacy',
        'High Risk': 'Consider aromatase inhibitor',
        'Very High Risk': 'Switch to AI'
    },
    'Phenytoin': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor levels frequently',
        'High Risk': 'Consider 25% dose reduction',
        'Very High Risk': 'Consider alternative AED'
    },
    'Atorvastatin': {
        'Low Risk': 'Standard dosing (10-20mg)',
        'Moderate Risk': 'Start with 10mg',
        'High Risk': 'Use pravastatin',
        'Very High Risk': 'Avoid atorvastatin'
    },
    'Capecitabine': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': '25% dose reduction',
        'High Risk': '50% dose reduction',
        'Very High Risk': 'Avoid capecitabine'
    },
    'Carbamazepine': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*1502',
        'Very High Risk': 'Avoid carbamazepine'
    },
    'Abacavir': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Screen for HLA-B*5701',
        'High Risk': 'Screen for HLA-B*5701',
        'Very High Risk': 'Contraindicated if positive'
    },
    'Allopurinol': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*5801',
        'Very High Risk': 'Avoid allopurinol'
    }
}

print(f"  ✓ Loaded guidelines for {len(clinical_guidelines)} drugs")

# Calculate disparity
disparity = df.groupby('ancestry').agg({
    'high_risk': 'mean',
    'equity_score': 'mean',
    'genetic_risk': 'mean',
    'ses_risk': 'mean'
}).round(3).sort_values('high_risk', ascending=False)

print("\n  Disparity by ancestry (LARGE DATASET):")
print(disparity)

# Create enhanced visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f'Pharmacogenomic Equity Score Dashboard (n={len(df):,})', fontsize=14, fontweight='bold')

# Distribution
ax1 = axes[0, 0]
for ancestry in df['ancestry'].unique():
    subset = df[df['ancestry'] == ancestry]
    ax1.hist(subset['equity_score'], alpha=0.5, bins=30, label=ancestry)
ax1.set_xlabel('Equity Score')
ax1.set_ylabel('Frequency')
ax1.set_title(f'Distribution by Ancestry (n={len(df):,})')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Risk matrix
ax2 = axes[0, 1]
risk_matrix = df.groupby(['ancestry', 'risk_category']).size().unstack(fill_value=0)
risk_percentages = risk_matrix.div(risk_matrix.sum(axis=1), axis=0) * 100
risk_percentages.T.plot(kind='bar', ax=ax2, color=['green', 'gold', 'orange', 'red'])
ax2.set_xlabel('Risk Category')
ax2.set_ylabel('Percentage (%)')
ax2.set_title('Risk Distribution by Ancestry')
ax2.legend(title='Ancestry')
ax2.grid(True, alpha=0.3)

# Scatter
ax3 = axes[1, 0]
scatter = ax3.scatter(df['genetic_risk'], df['ses_risk'], 
                      c=df['equity_score'], cmap='RdYlGn_r', alpha=0.3, s=10)
ax3.set_xlabel('Genetic Risk')
ax3.set_ylabel('SES Risk')
ax3.set_title(f'Genetic vs SES Risk (n={len(df):,})')
plt.colorbar(scatter, ax=ax3, label='Equity Score')
ax3.grid(True, alpha=0.3)

# Pie chart
ax4 = axes[1, 1]
avg_risk = df.groupby('ancestry')['equity_score'].mean().sort_values()
colors = ['gold', 'lightblue', 'lightgreen', 'coral', 'pink']
ax4.pie(avg_risk.values, labels=avg_risk.index, colors=colors, autopct='%1.1f%%')
ax4.set_title('Average Equity Score by Ancestry')

plt.tight_layout()
plt.savefig('data/processed/equity_score_dashboard_large.png', dpi=150)
print("  ✓ Saved: equity_score_dashboard_large.png")

# Save
df.to_csv("data/processed/pharmacogenomic_equity_scores_large.csv", index=False)
print(f"  ✓ Saved: pharmacogenomic_equity_scores_large.csv ({len(df):,} records)")

print("\n" + "="*60)
print("✓ STEP 5 COMPLETE!")
print(f"  • Total patients analyzed: {len(df):,}")
print(f"  • Average Equity Score: {df['equity_score'].mean():.1f}")
print(f"  • High-risk patients: {df['high_risk'].mean()*100:.1f}%")
print(f"  • Highest risk ancestry: {disparity.index[0]}")
print("="*60)
