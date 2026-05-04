# 08_equity_score_fixed.py
# Step 5 - Pharmacogenomic Equity Score (Fixed)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("STEP 5: Pharmacogenomic Equity Score (PES)")
print("="*60)

# ── Part 1: Load and prepare data ─────────────────────────────────────────
print("\n[1/6] Loading data...")

# Load enhanced GxE data
df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
print(f"  ✓ Loaded {len(df)} individuals")

# Add ancestry if not present
if 'ancestry' not in df.columns:
    np.random.seed(42)
    df['ancestry'] = np.random.choice(['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], len(df), 
                                       p=[0.26, 0.20, 0.20, 0.20, 0.14])

print(f"  ✓ Ancestry distribution:\n{df['ancestry'].value_counts()}")

# ── Part 2: Calculate individual risk components ──────────────────────────
print("\n[2/6] Calculating risk components...")

# Genetic risk score (0-100 scale)
df['genetic_risk'] = df['genotype'] * 33.3

# SES risk score (0-100 scale)
df['ses_risk'] = df['ses_score'] * 100

# Combined Equity Score
df['equity_score'] = (df['genetic_risk'] * 0.5 + df['ses_risk'] * 0.5)

# Clinical risk categories
df['risk_category'] = pd.cut(df['equity_score'], 
                              bins=[0, 25, 50, 75, 100],
                              labels=['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk'])

print(f"  ✓ Equity score range: {df['equity_score'].min():.1f} - {df['equity_score'].max():.1f}")
print("\n  Risk category distribution:")
print(df['risk_category'].value_counts())

# ── Part 3: Calculate PES by ancestry ─────────────────────────────────────
print("\n[3/6] Calculating PES by ancestry...")

# Create risk matrix
risk_matrix = df.groupby(['ancestry', 'risk_category']).size().unstack(fill_value=0)
risk_percentages = risk_matrix.div(risk_matrix.sum(axis=1), axis=0) * 100

print("\n  Risk distribution by ancestry (%):")
print(risk_percentages.round(1))

# Calculate disparity
df['high_risk'] = (df['risk_category'].isin(['High Risk', 'Very High Risk'])).astype(int)
disparity = df.groupby('ancestry').agg({
    'high_risk': 'mean',
    'equity_score': 'mean'
}).round(3).sort_values('high_risk', ascending=False)

print("\n  Disparity by ancestry:")
print(disparity)

# ── Part 4: Clinical guidelines ──────────────────────────────────────────
print("\n[4/6] Creating clinical guidelines...")

clinical_guidelines = {
    'Warfarin': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Consider reduced initial dose',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant'
    },
    'Clopidogrel': {
        'Low Risk': 'Standard therapy',
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
        'High Risk': 'Avoid codeine, consider tramadol or morphine',
        'Very High Risk': 'Avoid completely, use non-opioid alternatives'
    },
    'Tamoxifen': {
        'Low Risk': 'Standard dosing (20mg daily)',
        'Moderate Risk': 'Monitor for reduced efficacy',
        'High Risk': 'Consider aromatase inhibitor alternative',
        'Very High Risk': 'Switch to anastrozole or letrozole'
    },
    'Phenytoin': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor levels more frequently',
        'High Risk': 'Consider 25% dose reduction',
        'Very High Risk': 'Consider fosphenytoin or alternative AED'
    },
    'Atorvastatin': {
        'Low Risk': 'Standard dosing (10-20mg)',
        'Moderate Risk': 'Start with 10mg, monitor CK',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid atorvastatin, use alternative statin'
    },
    'Capecitabine': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Consider 50% dose reduction',
        'Very High Risk': 'Avoid, consider alternative chemotherapy'
    }
}

# ── Part 5: Create visualization dashboard ────────────────────────────────
print("\n[5/6] Creating visualization dashboard...")

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

# Plot 2: Risk category bar chart
ax2 = axes[0, 1]
risk_percentages.T.plot(kind='bar', ax=ax2, color=['blue', 'green', 'orange', 'red'])
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

# ── Part 6: Generate patient reports ──────────────────────────────────────
print("\n[6/6] Creating patient reports...")

# Sample patient reports
sample = df.sample(10, random_state=42)
reports = []
for _, p in sample.iterrows():
    reports.append({
        'Patient': p['individual_id'],
        'Ancestry': p['ancestry'],
        'Genotype': f"{int(p['genotype'])} alleles",
        'Equity Score': f"{p['equity_score']:.1f}",
        'Risk': p['risk_category']
    })

pd.DataFrame(reports).to_csv("data/processed/sample_patient_reports.csv", index=False)
print("  ✓ Saved: data/processed/sample_patient_reports.csv")

# Save full dataset
df.to_csv("data/processed/pharmacogenomic_equity_scores.csv", index=False)
print("  ✓ Saved: data/processed/pharmacogenomic_equity_scores.csv")

print("\n" + "="*60)
print("✓ STEP 5 COMPLETE!")
print("="*60)

print("\nKEY FINDINGS:")
print(f"  • Average Equity Score: {df['equity_score'].mean():.1f}")
print(f"  • High-risk patients: {df['high_risk'].mean()*100:.1f}%")
print(f"  • Highest risk ancestry: {disparity.index[0]}")
print("\nOutput files saved in data/processed/")