# 09_web_atlas_v2.py - Uses central drug configuration

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from drug_config import DRUG_DATABASE, get_drug_list, get_drug_class

print("="*60)
print("STEP 6: Interactive Web Atlas (v2 - Central Config)")
print("="*60)

# Load data
df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded {len(df)} patient records")

# Helper function for ancestry descriptions
def get_ancestry_description(ancestry):
    descriptions = {'AFR': 'African', 'EUR': 'European', 'EAS': 'East Asian', 
                    'SAS': 'South Asian', 'AMR': 'Admixed American'}
    return descriptions.get(ancestry, ancestry)

# Build guidelines dictionary from central config
guidelines = {}
for drug_name, drug_info in DRUG_DATABASE.items():
    guidelines[drug_name] = {
        'Low Risk': drug_info['low_risk'],
        'Moderate Risk': drug_info['moderate_risk'],
        'High Risk': drug_info['high_risk'],
        'Very High Risk': drug_info['very_high_risk']
    }

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs from central config")

# Initialize Dash app
app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")
server = app.server

# Rest of your app layout remains the same...
# (Copy your existing layout here, but the guidelines are now auto-generated)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
