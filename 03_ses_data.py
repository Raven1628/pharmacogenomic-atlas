# 03_ses_data.py
# Step 1C - SES Proxy Data

import pandas as pd
import numpy as np
import os

print("="*60)
print("STEP 1C: Creating SES Proxy Data")
print("="*60)

# ── Part 1: Create directories ─────────────────────────────────────────────
os.makedirs("data/processed", exist_ok=True)

# ── Part 2: Create realistic simulated SES data ───────────────────────────
print("\n[1/2] Creating realistic SES dataset...")

np.random.seed(42)
n_counties = 3142  # Number of US counties

# Generate realistic SES metrics with correlations
# Poverty rate (0-30%, skewed toward lower values)
poverty_rate = np.random.beta(2, 5, n_counties) * 30

# Unemployment rate (correlated with poverty, 0-15%)
unemployment_rate = 2 + poverty_rate * 0.3 + np.random.normal(0, 1.5, n_counties)
unemployment_rate = np.clip(unemployment_rate, 0, 20)

# No high school diploma (correlated with poverty, 0-35%)
no_hs_diploma = 5 + poverty_rate * 0.5 + np.random.normal(0, 2, n_counties)
no_hs_diploma = np.clip(no_hs_diploma, 0, 40)

# Create state assignments (each state gets roughly proportional counties)
states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
          'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
          'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
          'VA', 'WA', 'WV', 'WI', 'WY']

# Assign states randomly but with realistic weights (larger states get more counties)
state_weights = [1, 0.3, 0.7, 0.6, 5, 3, 0.4, 0.3, 2, 2, 0.2, 0.5, 2, 1.5, 1,
                 1, 1.5, 1.5, 0.3, 0.5, 1, 2, 1, 1.5, 1.5, 0.5, 0.5, 0.6, 0.2, 0.5,
                 0.8, 2, 1.2, 0.3, 2, 1, 0.8, 2, 0.3, 1, 0.5, 2, 3, 0.4, 0.2,
                 1.5, 1.5, 0.5, 0.8, 0.3]

state_weights = np.array(state_weights) / sum(state_weights)
assigned_states = np.random.choice(states, n_counties, p=state_weights)

# Create county names
county_names = [f"County_{i}" for i in range(n_counties)]

# Create DataFrame
census_df = pd.DataFrame({
    'county': county_names,
    'state': assigned_states,
    'poverty_rate': np.round(poverty_rate, 1),
    'unemployment_rate': np.round(unemployment_rate, 1),
    'no_hs_diploma': np.round(no_hs_diploma, 1)
})

print(f"  ✓ Created data for {len(census_df):,} counties")
print(f"  ✓ States represented: {census_df['state'].nunique()}")
print(f"\n  Summary statistics:")
print(f"    Poverty rate: mean={census_df['poverty_rate'].mean():.1f}%, median={census_df['poverty_rate'].median():.1f}%")
print(f"    Unemployment: mean={census_df['unemployment_rate'].mean():.1f}%, median={census_df['unemployment_rate'].median():.1f}%")
print(f"    No HS diploma: mean={census_df['no_hs_diploma'].mean():.1f}%, median={census_df['no_hs_diploma'].median():.1f}%")

# ── Part 3: Create vulnerability scores ────────────────────────────────────
print("\n[2/3] Calculating vulnerability scores...")

# Create percentiles (0-1 scale, higher = more vulnerable)
census_df['poverty_percentile'] = census_df['poverty_rate'].rank(pct=True)
census_df['unemployment_percentile'] = census_df['unemployment_rate'].rank(pct=True)
census_df['education_percentile'] = census_df['no_hs_diploma'].rank(pct=True)

# Composite vulnerability score (average of percentiles)
census_df['SES_composite'] = (
    census_df['poverty_percentile'] + 
    census_df['unemployment_percentile'] + 
    census_df['education_percentile']
) / 3

# Create quartiles
census_df['SES_quartile'] = pd.qcut(
    census_df['SES_composite'], 
    q=4, 
    labels=['Q1_LeastVulnerable', 'Q2', 'Q3', 'Q4_MostVulnerable']
)

# Binary indicator for high vulnerability
census_df['high_vulnerability'] = (census_df['SES_quartile'] == 'Q4_MostVulnerable').astype(int)

print(f"  ✓ SES quartile distribution:")
print(census_df['SES_quartile'].value_counts())

# ── Part 4: State-level summary ───────────────────────────────────────────
print("\n[3/4] Creating state-level summary...")

state_summary = census_df.groupby('state').agg({
    'SES_composite': ['mean', 'std'],
    'poverty_rate': 'mean',
    'unemployment_rate': 'mean',
    'no_hs_diploma': 'mean',
    'high_vulnerability': 'mean'
}).round(3)

state_summary.columns = ['mean_vulnerability', 'std_vulnerability', 'mean_poverty', 
                          'mean_unemployment', 'mean_no_hs', 'prop_high_vulnerability']
state_summary = state_summary.sort_values('mean_vulnerability', ascending=False)

print("\n  Top 5 most vulnerable states:")
print(state_summary.head(5))

print("\n  Bottom 5 least vulnerable states:")
print(state_summary.tail(5))

# ── Part 5: Save outputs ──────────────────────────────────────────────────
print("\n[4/4] Saving outputs...")

# Save full dataset
census_df.to_csv("data/processed/county_ses_data.csv", index=False)
print("  ✓ Saved: data/processed/county_ses_data.csv")

# Create simplified version for integration
ses_simplified = census_df[['state', 'poverty_rate', 'unemployment_rate', 
                             'no_hs_diploma', 'SES_composite', 'SES_quartile', 
                             'high_vulnerability']].copy()
ses_simplified.to_csv("data/processed/ses_simplified.csv", index=False)
print("  ✓ Saved: data/processed/ses_simplified.csv")

# Save state summary
state_summary.to_csv("data/processed/svi_state_summary.csv")
print("  ✓ Saved: data/processed/svi_state_summary.csv")

print("\n" + "="*60)
print("✓ STEP 1C COMPLETE!")
print("="*60)
print("\nOutput files:")
print("  • data/processed/county_ses_data.csv - County-level SES metrics")
print("  • data/processed/ses_simplified.csv - Simplified for integration")
print("  • data/processed/svi_state_summary.csv - Vulnerability by state")
print("\nKey SES variables created:")
print("  • SES_composite - Overall vulnerability score (0-1, higher = more vulnerable)")
print("  • SES_quartile - Vulnerability quartile (Q1 least to Q4 most vulnerable)")
print("  • high_vulnerability - Binary indicator for top quartile")
print("  • poverty_rate, unemployment_rate, no_hs_diploma - Individual metrics")