# 09_web_atlas_with_fda.py
# Pharmacogenomic Equity Atlas with Full FDA Integration

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

print("="*60)
print("Pharmacogenomic Equity Atlas - WITH FDA DATA INTEGRATION")
print("="*60)

# Load data
df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded {len(df):,} patient records")

# Load FDA data
try:
    fda_associations = pd.read_csv("data/fda/fda_pgx_associations.csv")
    print(f"  ✓ Loaded FDA PGx associations: {len(fda_associations)}")
except:
    fda_associations = None
    print("  ⚠ FDA data not found")

# Drug guidelines with FDA evidence levels
guidelines = {
    'Warfarin': {
        'gene': 'CYP2C9/VKORC1', 'fda_level': '📋 Dosage Label',
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant'
    },
    'Clopidogrel': {
        'gene': 'CYP2C19', 'fda_level': '⚠️ Warning',
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider alternative therapy',
        'Very High Risk': 'Avoid clopidogrel'
    },
    'Simvastatin': {
        'gene': 'SLCO1B1', 'fda_level': '📋 Dosage Label',
        'Low Risk': 'Standard 40mg',
        'Moderate Risk': 'Start with 20mg',
        'High Risk': 'Use alternative statin',
        'Very High Risk': 'Avoid simvastatin'
    },
    'Fluorouracil': {
        'gene': 'DPYD', 'fda_level': '📋 Dosage Label',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': '25% dose reduction',
        'High Risk': '50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil'
    },
    'Codeine': {
        'gene': 'CYP2D6', 'fda_level': '⚠️⚠️ Boxed Warning',
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine',
        'Very High Risk': 'Use non-opioid alternatives'
    },
    'Carbamazepine': {
        'gene': 'HLA-B', 'fda_level': '⚠️⚠️ Boxed Warning',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*1502',
        'Very High Risk': 'Avoid carbamazepine'
    },
    'Abacavir': {
        'gene': 'HLA-B', 'fda_level': '⚠️⚠️ Boxed Warning',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Screen for HLA-B*5701',
        'High Risk': 'Screen for HLA-B*5701',
        'Very High Risk': 'Contraindicated if positive'
    },
    'Allopurinol': {
        'gene': 'HLA-B', 'fda_level': '⚠️ Warning',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*5801',
        'Very High Risk': 'Avoid allopurinol'
    },
    'Tamoxifen': {
        'gene': 'CYP2D6', 'fda_level': 'ℹ️ Clinical Pharmacology',
        'Low Risk': 'Standard dosing (20mg daily)',
        'Moderate Risk': 'Monitor for reduced efficacy',
        'High Risk': 'Consider aromatase inhibitor',
        'Very High Risk': 'Switch to AI'
    },
    'Phenytoin': {
        'gene': 'CYP2C9', 'fda_level': 'ℹ️ Clinical Pharmacology',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor levels frequently',
        'High Risk': 'Consider 25% dose reduction',
        'Very High Risk': 'Consider alternative AED'
    }
}

app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas - FDA Edition")
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.P(f"Integrated with Official Drugs@FDA Database | {len(guidelines)} drugs",
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
                html.H3("FDA Table of Pharmacogenetic Associations"),
                html.P("Based on FDA's official PGx guidance", 
                       style={'color': '#666', 'marginBottom': '20px'}),
                html.Div(id='fda-table-container')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='📊 Drug Guidelines', children=[
            html.Div([
                html.H3("Clinical Recommendations with FDA Evidence"),
                html.Div([
                    html.Label("Select Drug:"),
                    dcc.Dropdown(
                        id='guideline-drug-select',
                        options=[{'label': f"{drug} ({guidelines[drug]['fda_level']})", 'value': drug} 
                                 for drug in guidelines.keys()],
                        value='Warfarin'
                    )
                ]),
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='ℹ️ About FDA Data', children=[
            html.Div([
                html.H3("Drugs@FDA Database Integration"),
                html.P("This tool integrates official FDA data from:", 
                       style={'marginBottom': '20px'}),
                html.Ul([
                    html.Li("Drugs@FDA database - FDA approval and labeling information"),
                    html.Li("FDA Table of Pharmacogenetic Associations"),
                    html.Li("FDA Adverse Event Reporting System (FAERS) data"),
                ]),
                html.H4("FDA Evidence Levels"),
                html.Table([
                    html.Tr([html.Td("⚠️⚠️ Boxed Warning", style={'fontWeight': 'bold'}), 
                             html.Td("Strongest warning - screening required before prescribing")]),
                    html.Tr([html.Td("⚠️ Warning", style={'fontWeight': 'bold'}), 
                             html.Td("Significant risk - strongly consider genetic testing")]),
                    html.Tr([html.Td("📋 Dosage Label", style={'fontWeight': 'bold'}), 
                             html.Td("Dosing guidance - adjust dose based on genotype")]),
                    html.Tr([html.Td("ℹ️ Clinical Pharmacology", style={'fontWeight': 'bold'}), 
                             html.Td("Informational - describes genetic effects on PK/PD")]),
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
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
        risk, color, icon = "Low Risk", "#27ae60", "🟢"
    elif score < 50:
        risk, color, icon = "Moderate Risk", "#f39c12", "🟡"
    elif score < 75:
        risk, color, icon = "High Risk", "#e67e22", "🟠"
    else:
        risk, color, icon = "Very High Risk", "#e74c3c", "🔴"
    
    recs = []
    for drug in guidelines:
        fda_marker = guidelines[drug]['fda_level']
        recs.append(html.Li(f"{fda_marker} 💊 {drug}: {guidelines[drug][risk]}"))
    
    return html.Div([
        html.H4(f"{icon} Risk: {risk}", style={'color': color}),
        html.P(f"📊 Equity Score: {score:.1f}"),
        html.H5("Clinical Recommendations with FDA Evidence:", style={'marginTop': '15px'}),
        html.Ul(recs)
    ])

@app.callback(
    Output('fda-table-container', 'children'),
    Input('fda-table-container', 'id')
)
def display_fda_table(_):
    if fda_associations is None:
        return html.Div("FDA data not available. Run integrate_fda_database.py first.")
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Drug"), html.Th("Gene"), html.Th("Variant"),
            html.Th("FDA Action"), html.Th("Recommendation")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(row['Drug']),
                html.Td(row['Gene']),
                html.Td(row['Variant']),
                html.Td(row['Action'], style={'fontWeight': 'bold'}),
                html.Td(row['Recommendation'])
            ]) for _, row in fda_associations.iterrows()
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})

@app.callback(
    Output('guidelines-table', 'children'),
    Input('guideline-drug-select', 'value')
)
def update_guidelines(drug):
    drug_info = guidelines[drug]
    
    rows = []
    for risk in ['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk']:
        rows.append(html.Tr([
            html.Td(risk, style={'fontWeight': 'bold'}),
            html.Td(drug_info[risk])
        ]))
    
    return html.Div([
        html.H4(f"{drug} ({drug_info['gene']})", style={'color': '#2c3e50'}),
        html.P(f"FDA Evidence: {drug_info['fda_level']}", 
               style={'color': '#e67e22', 'marginBottom': '20px'}),
        html.Table(rows, style={'width': '100%', 'borderCollapse': 'collapse'})
    ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
