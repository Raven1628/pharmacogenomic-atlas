# 09_web_atlas.py
# Pharmacogenomic Equity Atlas with Full FDA Data Integration

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

print("="*60)
print("Pharmacogenomic Equity Atlas - WITH FDA DATA INTEGRATION")
print("="*60)

# ============================================================
# 1. LOAD ALL DATA
# ============================================================
print("\n[1/5] Loading data...")

# Load equity scores
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
    print(f"  ✓ Loaded {len(df):,} patient records")
except:
    df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
    print(f"  ✓ Loaded {len(df):,} records")

# Load FDA PGx associations
try:
    fda_df = pd.read_csv("data/fda/fda_pgx_associations.csv")
    print(f"  ✓ Loaded FDA PGx associations: {len(fda_df)} drugs")
except:
    # Create FDA data if not available
    fda_df = pd.DataFrame([
        {"Drug": "Abacavir", "Gene": "HLA-B", "Variant": "HLA-B*57:01", 
         "FDA_Action": "Boxed Warning", "Recommendation": "Screen before use; contraindicated if positive"},
        {"Drug": "Carbamazepine", "Gene": "HLA-B", "Variant": "HLA-B*15:02", 
         "FDA_Action": "Boxed Warning", "Recommendation": "Screen in at-risk populations; avoid if positive"},
        {"Drug": "Clopidogrel", "Gene": "CYP2C19", "Variant": "CYP2C19*2/*3", 
         "FDA_Action": "Warning", "Recommendation": "Consider alternative therapy in poor metabolizers"},
        {"Drug": "Warfarin", "Gene": "CYP2C9/VKORC1", "Variant": "CYP2C9*2/*3", 
         "FDA_Action": "Dosage Label", "Recommendation": "Use genotype-guided initial dosing"},
        {"Drug": "Codeine", "Gene": "CYP2D6", "Variant": "Ultrarapid metabolizer", 
         "FDA_Action": "Boxed Warning", "Recommendation": "Contraindicated in children; avoid in ultrarapid metabolizers"},
        {"Drug": "Simvastatin", "Gene": "SLCO1B1", "Variant": "SLCO1B1*5", 
         "FDA_Action": "Dosage Label", "Recommendation": "Consider lower dose or alternative statin"},
        {"Drug": "Fluorouracil", "Gene": "DPYD", "Variant": "DPYD*2A", 
         "FDA_Action": "Dosage Label", "Recommendation": "Consider dose reduction in intermediate metabolizers"},
        {"Drug": "Tamoxifen", "Gene": "CYP2D6", "Variant": "Poor metabolizer", 
         "FDA_Action": "Clinical Pharmacology", "Recommendation": "Consider alternative hormonal therapy"},
        {"Drug": "Allopurinol", "Gene": "HLA-B", "Variant": "HLA-B*58:01", 
         "FDA_Action": "Warning", "Recommendation": "Consider screening in high-risk populations"},
    ])
    print(f"  ✓ Created FDA reference data: {len(fda_df)} drugs")

# Load UMAP coordinates if available
try:
    umap_df = pd.read_csv("data/processed/umap_coordinates.csv")
    print(f"  ✓ Loaded UMAP coordinates for {len(umap_df):,} samples")
    umap_available = True
except:
    umap_available = False
    print("  ⚠ UMAP coordinates not available")

# ============================================================
# 2. DRUG GUIDELINES WITH FDA EVIDENCE
# ============================================================
print("\n[2/5] Loading drug guidelines with FDA evidence...")

# Drug guidelines with FDA evidence levels
guidelines = {
    'Warfarin': {
        'gene': 'CYP2C9/VKORC1',
        'fda_level': '📋 Dosage Label',
        'fda_action': 'Dose adjustment based on genotype',
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant'
    },
    'Clopidogrel': {
        'gene': 'CYP2C19',
        'fda_level': '⚠️ Warning',
        'fda_action': 'Alternative therapy for poor metabolizers',
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider alternative therapy (ticagrelor)',
        'Very High Risk': 'Avoid clopidogrel'
    },
    'Simvastatin': {
        'gene': 'SLCO1B1',
        'fda_level': '📋 Dosage Label',
        'fda_action': 'Lower dose or alternative statin',
        'Low Risk': 'Standard 40mg daily',
        'Moderate Risk': 'Start with 20mg, monitor CK',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid simvastatin'
    },
    'Fluorouracil': {
        'gene': 'DPYD',
        'fda_level': '📋 Dosage Label',
        'fda_action': 'Dose reduction based on DPYD status',
        'Low Risk': 'Standard dosing (500mg/m²)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Consider 50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil'
    },
    'Codeine': {
        'gene': 'CYP2D6',
        'fda_level': '⚠️⚠️ Boxed Warning',
        'fda_action': 'Contraindicated in children and ultrarapid metabolizers',
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine, consider tramadol',
        'Very High Risk': 'Use non-opioid alternatives'
    },
    'Carbamazepine': {
        'gene': 'HLA-B',
        'fda_level': '⚠️⚠️ Boxed Warning',
        'fda_action': 'Screen for HLA-B*1502 in at-risk populations',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*1502 allele',
        'Very High Risk': 'Avoid carbamazepine, use alternative'
    },
    'Abacavir': {
        'gene': 'HLA-B',
        'fda_level': '⚠️⚠️ Boxed Warning',
        'fda_action': 'Screen for HLA-B*5701 before prescribing',
        'Low Risk': 'Standard dosing (600mg daily)',
        'Moderate Risk': 'Screen for HLA-B*5701',
        'High Risk': 'Screen for HLA-B*5701',
        'Very High Risk': 'Contraindicated if HLA-B*5701 positive'
    },
    'Tamoxifen': {
        'gene': 'CYP2D6',
        'fda_level': 'ℹ️ Clinical Pharmacology',
        'fda_action': 'Consider alternative therapy for poor metabolizers',
        'Low Risk': 'Standard dosing (20mg daily)',
        'Moderate Risk': 'Monitor for reduced efficacy',
        'High Risk': 'Consider aromatase inhibitor',
        'Very High Risk': 'Switch to anastrozole or letrozole'
    },
    'Allopurinol': {
        'gene': 'HLA-B',
        'fda_level': '⚠️ Warning',
        'fda_action': 'Screen for HLA-B*5801 in high-risk populations',
        'Low Risk': 'Standard dosing (100-300mg daily)',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*5801 allele',
        'Very High Risk': 'Avoid allopurinol, use alternative'
    },
    'Phenytoin': {
        'gene': 'CYP2C9',
        'fda_level': 'ℹ️ Clinical Pharmacology',
        'fda_action': 'Dose adjustment for CYP2C9 poor metabolizers',
        'Low Risk': 'Standard dosing (300-400mg daily)',
        'Moderate Risk': 'Monitor levels frequently',
        'High Risk': 'Consider 25% dose reduction',
        'Very High Risk': 'Consider alternative anticonvulsant'
    }
}

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs with FDA evidence")

# ============================================================
# 3. CREATE DASH APP
# ============================================================
print("\n[3/5] Creating Dash application...")

app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas - FDA Edition")
server = app.server

# Helper function
def get_ancestry_description(ancestry):
    descriptions = {'AFR': 'African', 'EUR': 'European', 'EAS': 'East Asian',
                    'SAS': 'South Asian', 'AMR': 'Admixed American'}
    return descriptions.get(ancestry, ancestry)

# ============================================================
# 4. APP LAYOUT
# ============================================================
app.layout = html.Div([
    # Header with FDA badge
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.Div([
            html.Span("🔬 FDA Pharmacogenetic Data Integrated", 
                      style={'backgroundColor': '#1a56db', 'color': 'white', 
                             'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '14px'})
        ], style={'textAlign': 'center', 'marginBottom': '10px'}),
        html.P(f"Analyzing {len(df):,} patient records | {len(guidelines)} drugs with FDA guidance | 5 ancestry groups",
               style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'marginBottom': '30px'}),
    
    dcc.Tabs([
        # TAB 1: Clinical Calculator
        dcc.Tab(label='📊 Clinical Calculator', children=[
            html.Div([
                html.H3("Patient Risk Assessment Tool", style={'marginTop': '20px'}),
                
                # FDA Info Banner
                html.Div([
                    html.Span("ℹ️", style={'fontSize': '20px', 'marginRight': '10px'}),
                    html.Span("Recommendations incorporate FDA Boxed Warnings, Warnings, and Dosage Label information."),
                ], style={'backgroundColor': '#e8f4f8', 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.Label("Patient Ancestry:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='ancestry-input',
                            options=[{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                     for a in sorted(df['ancestry'].unique())],
                            placeholder='Select ancestry...'
                        )
                    ], style={'width': '30%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.Label("SES Vulnerability Score (0-1):", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.01, value=0.5,
                            marks={i/10: str(i/10) for i in range(0, 11)},
                            tooltip={"always_visible": True}
                        )
                    ], style={'width': '65%', 'display': 'inline-block', 'marginLeft': '20px'}),
                    
                    html.Div([
                        html.Label("Genetic Risk Score (0-100):", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='genetic-slider',
                            min=0, max=100, step=1, value=33,
                            marks={i: str(i) for i in range(0, 101, 10)},
                            tooltip={"always_visible": True}
                        )
                    ], style={'marginTop': '20px'})
                ]),
                
                html.Div(id='calculator-results', style={'marginTop': '20px', 'padding': '20px', 
                                                         'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
            ], style={'padding': '20px'})
        ]),
        
        # TAB 2: FDA Pharmacogenetic Table
        dcc.Tab(label='📋 FDA PGx Table', children=[
            html.Div([
                html.H3("FDA Table of Pharmacogenetic Associations", style={'marginTop': '20px'}),
                html.P("Based on FDA's official guidance for pharmacogenetic testing", 
                       style={'color': '#666', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Label("Filter by Drug:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='fda-filter',
                        options=[{'label': 'All Drugs', 'value': 'All'}] + 
                                [{'label': d, 'value': d} for d in sorted(fda_df['Drug'].unique())],
                        value='All'
                    )
                ], style={'width': '50%', 'marginBottom': '20px'}),
                
                html.Div(id='fda-table', style={'overflowX': 'auto'})
            ], style={'padding': '20px'})
        ]),
        
        # TAB 3: Drug Guidelines with FDA Evidence
        dcc.Tab(label='💊 Drug Guidelines', children=[
            html.Div([
                html.H3("Clinical Recommendations with FDA Evidence", style={'marginTop': '20px'}),
                
                html.Div([
                    html.Label("Select Drug:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='drug-select',
                        options=[{'label': f"{drug} - {guidelines[drug]['gene']}", 'value': drug} 
                                 for drug in guidelines.keys()],
                        value='Warfarin'
                    )
                ], style={'width': '50%', 'marginBottom': '20px'}),
                
                html.Div(id='drug-guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        # TAB 4: FDA Evidence Summary
        dcc.Tab(label='🏷️ FDA Evidence Levels', children=[
            html.Div([
                html.H3("Understanding FDA Evidence Levels", style={'marginTop': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H4("⚠️⚠️ Boxed Warning", style={'color': '#e74c3c'}),
                        html.P("Strongest FDA warning. Indicates serious or life-threatening risk. Genetic testing is REQUIRED before prescribing.", 
                               style={'marginLeft': '20px'}),
                        html.P("Examples: Abacavir (HLA-B*57:01), Carbamazepine (HLA-B*15:02), Codeine (CYP2D6)", 
                               style={'marginLeft': '20px', 'fontStyle': 'italic', 'color': '#666'})
                    ], style={'borderLeft': '5px solid #e74c3c', 'padding': '15px', 'margin': '15px 0', 'backgroundColor': '#fdedec'}),
                    
                    html.Div([
                        html.H4("⚠️ Warning", style={'color': '#e67e22'}),
                        html.P("Indicates significant risk. Strongly consider genetic testing before prescribing.", 
                               style={'marginLeft': '20px'}),
                        html.P("Examples: Clopidogrel (CYP2C19), Allopurinol (HLA-B*58:01)", 
                               style={'marginLeft': '20px', 'fontStyle': 'italic', 'color': '#666'})
                    ], style={'borderLeft': '5px solid #e67e22', 'padding': '15px', 'margin': '15px 0', 'backgroundColor': '#fdf2e9'}),
                    
                    html.Div([
                        html.H4("📋 Dosage Label", style={'color': '#3498db'}),
                        html.P("Dosing guidance based on genotype. Genetic testing recommended for optimal dosing.", 
                               style={'marginLeft': '20px'}),
                        html.P("Examples: Warfarin (CYP2C9/VKORC1), Simvastatin (SLCO1B1), Fluorouracil (DPYD)", 
                               style={'marginLeft': '20px', 'fontStyle': 'italic', 'color': '#666'})
                    ], style={'borderLeft': '5px solid #3498db', 'padding': '15px', 'margin': '15px 0', 'backgroundColor': '#e8f4f8'}),
                    
                    html.Div([
                        html.H4("ℹ️ Clinical Pharmacology", style={'color': '#2c3e50'}),
                        html.P("Informational section describing genetic effects on drug PK/PD. Testing may be considered.", 
                               style={'marginLeft': '20px'}),
                        html.P("Examples: Tamoxifen (CYP2D6), Metoprolol (CYP2D6)", 
                               style={'marginLeft': '20px', 'fontStyle': 'italic', 'color': '#666'})
                    ], style={'borderLeft': '5px solid #2c3e50', 'padding': '15px', 'margin': '15px 0', 'backgroundColor': '#ecf0f1'})
                ])
            ], style={'padding': '20px'})
        ]),
        
        # TAB 5: About
        
        dcc.Tab(label='📊 PCA Analysis', children=[
            html.Div([
                html.H3("Principal Component Analysis", style={'marginTop': '20px'}),
                html.P("PCA shows how genetic risk and SES vulnerability combine to create overall risk scores."),
                html.Img(src='/assets/pca_fixed.png', style={'width': '100%', 'borderRadius': '10px'}),
                html.P(f"PC1 explains 52.7% of variance, PC2 explains 33.6%", 
                       style={'fontSize': '12px', 'color': '#666', 'marginTop': '10px'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🗺️ UMAP Analysis', children=[
            html.Div([
                html.H3("UMAP Manifold Learning", style={'marginTop': '20px'}),
                html.P("UMAP reveals non-linear patterns in the data, often showing clearer separation of risk groups than PCA."),
                html.Img(src='/assets/umap_fixed.png', style={'width': '100%', 'borderRadius': '10px'}),
                html.P("UMAP preserves local structure, showing distinct clusters of patients with similar risk profiles",
                       style={'fontSize': '12px', 'color': '#666', 'marginTop': '10px'})
            ], style={'padding': '20px'})
        ]),
        
dcc.Tab(label='ℹ️ About', children=[
            html.Div([
                html.H3("About the Pharmacogenomic Equity Atlas", style={'marginTop': '20px'}),
                html.P("This tool integrates genetic, socioeconomic, and FDA pharmacogenetic data to guide personalized medicine."),
                
                html.H4("Data Sources:"),
                html.Ul([
                    html.Li("🏛️ FDA Table of Pharmacogenetic Associations"),
                    html.Li("🧬 1000 Genomes Project - Ancestry frequencies"),
                    html.Li("📊 gnomAD - Variant frequencies"),
                    html.Li("🏠 CDC SVI - Socioeconomic data"),
                    html.Li("📚 PharmGKB/CPIC - Clinical guidelines")
                ]),
                
                html.H4("FDA Evidence Levels:"),
                html.Ul([
                    html.Li("⚠️⚠️ Boxed Warning - Testing REQUIRED"),
                    html.Li("⚠️ Warning - Testing STRONGLY recommended"),
                    html.Li("📋 Dosage Label - Testing recommended"),
                    html.Li("ℹ️ Clinical Pharmacology - Testing may be considered")
                ]),
                
                html.H4("Supported Drugs:"),
                html.Div([
                    html.Ul([html.Li(drug) for drug in guidelines.keys()])
                ], style={'columnCount': 2}),
                
                html.Hr(),
                html.P("For clinical use only. Always consult a pharmacist.", 
                       style={'fontStyle': 'italic', 'color': '#666'})
            ], style={'padding': '20px'})
        ])
    ])
])

# ============================================================
# 5. CALLBACKS
# ============================================================
print("\n[4/5] Defining callbacks...")

@app.callback(
    Output('calculator-results', 'children'),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def update_calculator(ancestry, ses, genetic):
    if not ancestry:
        return html.Div("⚠️ Please select ancestry", style={'color': '#e74c3c'})
    
    equity_score = genetic * 0.5 + ses * 50
    
    if equity_score < 25:
        risk_category = "Low Risk"
        color = "#27ae60"
        icon = "🟢"
    elif equity_score < 50:
        risk_category = "Moderate Risk"
        color = "#f39c12"
        icon = "🟡"
    elif equity_score < 75:
        risk_category = "High Risk"
        color = "#e67e22"
        icon = "🟠"
    else:
        risk_category = "Very High Risk"
        color = "#e74c3c"
        icon = "🔴"
    
    recommendations = []
    for drug, info in guidelines.items():
        fda_marker = info['fda_level']
        rec = info[risk_category]
        recommendations.append(html.Li(f"{fda_marker} 💊 {drug}: {rec}"))
    
    return html.Div([
        html.H4(f"{icon} {risk_category}", style={'color': color}),
        html.P(f"📊 Equity Score: {equity_score:.1f}"),
        html.P(f"🌍 Ancestry: {ancestry} - {get_ancestry_description(ancestry)}"),
        html.P(f"🏠 SES Score: {ses:.2f}"),
        html.P(f"🧬 Genetic Risk: {genetic:.0f}"),
        html.H5("FDA-Informed Clinical Recommendations:", style={'marginTop': '15px'}),
        html.Ul(recommendations)
    ])

@app.callback(
    Output('fda-table', 'children'),
    Input('fda-filter', 'value')
)
def update_fda_table(filter_val):
    if filter_val == 'All':
        display_df = fda_df
    else:
        display_df = fda_df[fda_df['Drug'] == filter_val]
    
    # Create color-coded rows based on FDA action
    def get_row_color(action):
        if 'Boxed' in str(action):
            return '#fdedec'
        elif 'Warning' in str(action):
            return '#fdf2e9'
        elif 'Dosage' in str(action):
            return '#e8f4f8'
        else:
            return 'white'
    
    rows = []
    for _, row in display_df.iterrows():
        bg_color = get_row_color(row['FDA_Action'])
        rows.append(html.Tr([
            html.Td(row['Drug'], style={'backgroundColor': bg_color, 'padding': '10px'}),
            html.Td(row['Gene'], style={'backgroundColor': bg_color, 'padding': '10px'}),
            html.Td(row['Variant'], style={'backgroundColor': bg_color, 'padding': '10px'}),
            html.Td(row['FDA_Action'], style={'backgroundColor': bg_color, 'padding': '10px', 'fontWeight': 'bold'}),
            html.Td(row['Recommendation'], style={'backgroundColor': bg_color, 'padding': '10px'})
        ]))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Drug"), html.Th("Gene"), html.Th("Variant"), 
            html.Th("FDA Action"), html.Th("Recommendation")
        ], style={'backgroundColor': '#2c3e50', 'color': 'white'})),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})

@app.callback(
    Output('drug-guidelines-table', 'children'),
    Input('drug-select', 'value')
)
def update_drug_guidelines(drug):
    info = guidelines[drug]
    
    # Color code FDA level
    if 'Boxed' in info['fda_level']:
        fda_color = '#e74c3c'
    elif 'Warning' in info['fda_level']:
        fda_color = '#e67e22'
    elif 'Dosage' in info['fda_level']:
        fda_color = '#3498db'
    else:
        fda_color = '#2c3e50'
    
    rows = []
    for risk in ['Low Risk', 'Moderate Risk', 'High Risk', 'Very High Risk']:
        if risk == 'Low Risk':
            risk_color = '#27ae60'
        elif risk == 'Moderate Risk':
            risk_color = '#f39c12'
        elif risk == 'High Risk':
            risk_color = '#e67e22'
        else:
            risk_color = '#e74c3c'
        
        rows.append(html.Tr([
            html.Td(risk, style={'backgroundColor': risk_color, 'color': 'white', 'padding': '10px'}),
            html.Td(info[risk], style={'padding': '10px'})
        ]))
    
    # Check if this drug has FDA association
    fda_match = fda_df[fda_df['Drug'] == drug]
    fda_info = ""
    if len(fda_match) > 0:
        fda_info = html.Div([
            html.H5("FDA Pharmacogenetic Information:", style={'marginTop': '15px'}),
            html.P(f"📋 Variant: {fda_match.iloc[0]['Variant']}", style={'margin': '5px 0'}),
            html.P(f"⚠️ FDA Action: {fda_match.iloc[0]['FDA_Action']}", style={'margin': '5px 0'}),
            html.P(f"📝 Recommendation: {fda_match.iloc[0]['Recommendation']}", style={'margin': '5px 0'})
        ], style={'backgroundColor': '#e8f4f8', 'padding': '15px', 'borderRadius': '10px', 'marginTop': '20px'})
    
    return html.Div([
        html.Div([
            html.H3(f"{drug}", style={'display': 'inline-block', 'marginRight': '15px'}),
            html.Span(info['fda_level'], style={'backgroundColor': fda_color, 'color': 'white', 
                                                 'padding': '5px 10px', 'borderRadius': '20px', 'fontSize': '14px'})
        ], style={'marginBottom': '20px'}),
        
        html.P(f"Gene: {info['gene']}", style={'fontSize': '18px', 'marginBottom': '20px'}),
        html.P(f"FDA Action: {info['fda_action']}", style={'color': '#666', 'marginBottom': '20px'}),
        
        html.H4("Risk-Based Recommendations:"),
        html.Table(rows, style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'}),
        
        fda_info
    ])

# ============================================================
# 6. RUN THE APP
# ============================================================
print("\n[5/5] Starting web server...")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"\n🌐 Server running at http://localhost:{port}")
    print("📊 Features:")
    print("   • Clinical calculator with FDA-backed recommendations")
    print("   • Complete FDA PGx table with filtering")
    print("   • Drug guidelines with FDA evidence levels")
    print("   • Boxed Warning, Warning, and Dosage Label indicators")
    print("\n💡 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=False)
