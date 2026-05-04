# 09_web_atlas_fda.py
# Pharmacogenomic Equity Atlas with FDA Data Integration

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import os

print("="*60)
print("Pharmacogenomic Equity Atlas - WITH FDA DATA")
print("="*60)

# Load data
df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded {len(df):,} patient records")

# Load FDA data if available
try:
    fda_df = pd.read_csv("data/fda/fda_complete_pgx_table.csv")
    print(f"  ✓ Loaded FDA PGx data: {len(fda_df)} associations")
except:
    fda_df = None
    print("  ⚠ FDA data not found - run download_fda_data.py first")

# Drug guidelines with FDA evidence
guidelines = {
    'Warfarin': {
        'gene': 'CYP2C9/VKORC1',
        'fda_level': 'Dosage Label',
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant'
    },
    'Clopidogrel': {
        'gene': 'CYP2C19',
        'fda_level': 'Warning',
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider alternative therapy',
        'Very High Risk': 'Avoid clopidogrel'
    },
    'Simvastatin': {
        'gene': 'SLCO1B1',
        'fda_level': 'Dosage Label',
        'Low Risk': 'Standard 40mg',
        'Moderate Risk': 'Start with 20mg',
        'High Risk': 'Use alternative statin',
        'Very High Risk': 'Avoid simvastatin'
    },
    'Codeine': {
        'gene': 'CYP2D6',
        'fda_level': 'Boxed Warning',
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine',
        'Very High Risk': 'Use non-opioid alternatives'
    },
    'Carbamazepine': {
        'gene': 'HLA-B',
        'fda_level': 'Boxed Warning',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*1502',
        'Very High Risk': 'Avoid carbamazepine'
    },
    'Abacavir': {
        'gene': 'HLA-B',
        'fda_level': 'Boxed Warning',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Screen for HLA-B*5701',
        'High Risk': 'Screen for HLA-B*5701',
        'Very High Risk': 'Contraindicated if positive'
    },
    'Fluorouracil': {
        'gene': 'DPYD',
        'fda_level': 'Dosage Label',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': '25% dose reduction',
        'High Risk': '50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil'
    }
}

app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas - FDA Edition")
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.P(f"FDA Pharmacogenomic Data Integrated | {len(guidelines)} drugs | 5 ancestry groups",
               style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'marginBottom': '30px'}),
    
    dcc.Tabs([
        dcc.Tab(label='📊 Clinical Calculator', children=[
            html.Div([
                html.H3("Patient Risk Assessment Tool"),
                html.Div([
                    html.Div([
                        html.Label("Patient Ancestry:"),
                        dcc.Dropdown(
                            id='ancestry-input',
                            options=[{'label': a, 'value': a} for a in sorted(df['ancestry'].unique())],
                            placeholder='Select ancestry...'
                        )
                    ], style={'width': '30%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label("SES Vulnerability Score:"),
                        dcc.Slider(id='ses-slider', min=0, max=1, step=0.01, value=0.5,
                                  marks={i/10: str(i/10) for i in range(0, 11)})
                    ], style={'width': '65%', 'display': 'inline-block', 'marginLeft': '20px'}),
                    html.Div([
                        html.Label("Genetic Risk Score:"),
                        dcc.Slider(id='genetic-slider', min=0, max=100, step=1, value=33,
                                  marks={i: str(i) for i in range(0, 101, 10)})
                    ], style={'marginTop': '20px'})
                ]),
                html.Div(id='calculator-results', style={'marginTop': '20px', 'padding': '20px', 
                                                         'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='📋 FDA PGx Table', children=[
            html.Div([
                html.H3("FDA Pharmacogenetic Associations"),
                html.P("Based on FDA Table of Pharmacogenetic Associations"),
                html.Div([
                    html.Label("Filter by Drug:"),
                    dcc.Dropdown(id='fda-drug-filter', placeholder='Select drug...')
                ]),
                html.Div(id='fda-table-container', style={'marginTop': '20px', 'overflowX': 'auto'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='📊 Drug Guidelines', children=[
            html.Div([
                html.H3("Clinical Recommendations with FDA Evidence"),
                html.Div([
                    html.Label("Select Drug:"),
                    dcc.Dropdown(
                        id='guideline-drug-select',
                        options=[{'label': drug, 'value': drug} for drug in guidelines.keys()],
                        value='Warfarin'
                    )
                ]),
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ])
    ])
])

# Callbacks
@app.callback(
    Output('calculator-results', 'children'),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def update_calculator(ancestry, ses, genetic):
    if not ancestry:
        return html.Div("⚠️ Select ancestry", style={'color': '#e74c3c'})
    
    score = genetic * 0.5 + ses * 50
    if score < 25:
        risk, color = "Low Risk", "#27ae60"
    elif score < 50:
        risk, color = "Moderate Risk", "#f39c12"
    elif score < 75:
        risk, color = "High Risk", "#e67e22"
    else:
        risk, color = "Very High Risk", "#e74c3c"
    
    recs = [html.Li(f"💊 {drug}: {guidelines[drug][risk]} (FDA {guidelines[drug]['fda_level']})") 
            for drug in guidelines]
    
    return html.Div([
        html.H4(f"Risk: {risk}", style={'color': color}),
        html.P(f"Equity Score: {score:.1f}"),
        html.Ul(recs)
    ])

@app.callback(
    Output('fda-drug-filter', 'options'),
    Input('fda-drug-filter', 'id')
)
def set_fda_drug_options(_):
    if fda_df is not None:
        return [{'label': d, 'value': d} for d in fda_df['Drug'].unique()]
    return []

@app.callback(
    Output('fda-table-container', 'children'),
    Input('fda-drug-filter', 'value')
)
def update_fda_table(selected_drug):
    if fda_df is None:
        return html.Div("FDA data not available. Run download_fda_data.py first.")
    
    if selected_drug:
        filtered = fda_df[fda_df['Drug'] == selected_drug]
    else:
        filtered = fda_df
    
    return html.Table([
        html.Thead(html.Tr([html.Th(col) for col in filtered.columns])),
        html.Tbody([
            html.Tr([html.Td(str(val)) for val in row]) 
            for row in filtered.values
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})

@app.callback(
    Output('guidelines-table', 'children'),
    Input('guideline-drug-select', 'value')
)
def update_guidelines(drug):
    drug_info = guidelines[drug]
    fda_badge = f"🏷️ FDA: {drug_info['fda_level']}"
    
    rows = []
    for risk in ['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk']:
        rows.append(html.Tr([
            html.Td(risk, style={'fontWeight': 'bold'}),
            html.Td(drug_info[risk])
        ]))
    
    return html.Div([
        html.H4(f"{drug} ({drug_info['gene']})", style={'color': '#2c3e50'}),
        html.P(fda_badge, style={'color': '#e67e22', 'marginBottom': '20px'}),
        html.Table(rows, style={'width': '100%', 'borderCollapse': 'collapse'})
    ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
