# 08_equity_score.py
# Step 5 - Pharmacogenomic Equity Score (Uses central drug config)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from drug_config import DRUG_DATABASE, get_drug_list, get_drug_recommendation
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 5: Pharmacogenomic Equity Score (PES)")
print("="*60)

# Load data
df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
print(f"  ✓ Loaded {len(df)} individuals")

# Add ancestry if not present
if 'ancestry' not in df.columns:
    np.random.seed(42)
    df['ancestry'] = np.random.choice(['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], len(df), 
                                       p=[0.26, 0.20, 0.20, 0.20, 0.14])

# Calculate risk components
df['genetic_risk'] = df['genotype'] * 33.3
df['ses_risk'] = df['ses_score'] * 100
df['equity_score'] = (df['genetic_risk'] * 0.5 + df['ses_risk'] * 0.5)
df['risk_category'] = pd.cut(df['equity_score'], bins=[0, 25, 50, 75, 100],
                              labels=['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'])
df['high_risk'] = (df['risk_category'].isin(['High Risk', 'Very High Risk'])).astype(int)

# Build clinical guidelines from central config
clinical_guidelines = {}
for drug_name in get_drug_list():
    clinical_guidelines[drug_name] = {
        'Low Risk': get_drug_recommendation(drug_name, 'low_risk'),
        'Moderate Risk': get_drug_recommendation(drug_name, 'moderate_risk'),
        'High Risk': get_drug_recommendation(drug_name, 'high_risk'),
        'Very High Risk': get_drug_recommendation(drug_name, 'very_high_risk')
    }

print(f"  ✓ Loaded guidelines for {len(clinical_guidelines)} drugs from central config")

# Calculate disparity
disparity = df.groupby('ancestry').agg({
    'high_risk': 'mean',
    'equity_score': 'mean'
}).round(3).sort_values('high_risk', ascending=False)

print("\n  Disparity by ancestry:")
print(disparity)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Pharmacogenomic Equity Score (PES) Dashboard', fontsize=16, fontweight='bold')

# Plot 1: Equity score distribution
ax1 = axes[0, 0]
for ancestry in df['ancestry'].unique():
    subset = df[df['ancestry'] == ancestry]
    ax1.hist(subset['equity_score'], alpha=0.5, bins=20, label=ancestry)
ax1.set_xlabel('Equity Score')
ax1.set_ylabel('Frequency')
ax1.set_title('Distribution by Ancestry')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Risk category by ancestry
ax2 = axes[0, 1]
risk_matrix = df.groupby(['ancestry', 'risk_category']).size().unstack(fill_value=0)
risk_percentages = risk_matrix.div(risk_matrix.sum(axis=1), axis=0) * 100
risk_percentages.T.plot(kind='bar', ax=ax2, color=['green', 'gold', 'orange', 'red'])
ax2.set_xlabel('Risk Category')
ax2.set_ylabel('Percentage (%)')
ax2.set_title('Risk Distribution by Ancestry')
ax2.legend(title='Ancestry')
ax2.grid(True, alpha=0.3)

# Plot 3: Genetic vs SES scatter
ax3 = axes[1, 0]
scatter = ax3.scatter(df['genetic_risk'], df['ses_risk'], 
                      c=df['equity_score'], cmap='RdYlGn_r', alpha=0.5)
ax3.set_xlabel('Genetic Risk')
ax3.set_ylabel('SES Risk')
ax3.set_title('Genetic vs SES Risk')
plt.colorbar(scatter, ax=ax3, label='Equity Score')
ax3.grid(True, alpha=0.3)

# Plot 4: Risk by ancestry pie chart
ax4 = axes[1, 1]
avg_risk = df.groupby('ancestry')['equity_score'].mean().sort_values()
colors = ['gold', 'lightblue', 'lightgreen', 'coral', 'pink']
ax4.pie(avg_risk.values, labels=avg_risk.index, colors=colors, autopct='%1.1f%%')
ax4.set_title('Average Equity Score by Ancestry')

plt.tight_layout()
plt.savefig('data/processed/equity_score_dashboard.png', dpi=150)
print("  ✓ Saved: data/processed/equity_score_dashboard.png")

# Save outputs
df.to_csv("data/processed/pharmacogenomic_equity_scores.csv", index=False)
print("  ✓ Saved: data/processed/pharmacogenomic_equity_scores.csv")

print("\n" + "="*60)
print("✓ STEP 5 COMPLETE!")
print(f"  • Average Equity Score: {df['equity_score'].mean():.1f}")
print(f"  • High-risk patients: {df['high_risk'].mean()*100:.1f}%")
print(f"  • Highest risk ancestry: {disparity.index[0]}")
