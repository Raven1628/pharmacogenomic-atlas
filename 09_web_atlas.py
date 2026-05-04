# ============================================================
# PHARMACOGENOMIC EQUITY ATLAS - CLEAN VERSION
# No FDA labels - Simple and clean interface
# ============================================================

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("PHARMACOGENOMIC EQUITY ATLAS - CLEAN VERSION")
print("="*60)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("\n[1/4] Loading data...")

# Load primary dataset
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores_fixed.csv")
    print(f"  ✓ Loaded fixed dataset: {len(df):,} records")
except:
    try:
        df = pd.read_csv("data/processed/pharmacogenomic_equity_scores_large.csv")
        print(f"  ✓ Loaded large dataset: {len(df):,} records")
    except:
        try:
            df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
            print(f"  ✓ Loaded standard dataset: {len(df):,} records")
        except:
            df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
            np.random.seed(42)
            df['ancestry'] = np.random.choice(['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], len(df), 
                                               p=[0.26, 0.20, 0.20, 0.20, 0.14])
            df['equity_score'] = df['genotype'] * 33.3
            df['high_risk'] = (df['equity_score'] > 50).astype(int)
            df['ses_score'] = np.random.uniform(0, 1, len(df))
            df['genetic_risk'] = df['genotype'] * 33.3
            df['ses_risk'] = df['ses_score'] * 100
            print(f"  ✓ Loaded fallback dataset: {len(df):,} records")

dataset_size = len(df)

# ============================================================
# 2. DRUG DATABASE (NO FDA LABELS)
# ============================================================
print("\n[2/4] Loading drug database...")

# Simple drug database - no FDA labels
drugs_db = {
    'Warfarin': {
        'gene': 'CYP2C9',
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant (apixaban, rivaroxaban)'
    },
    'Clopidogrel': {
        'gene': 'CYP2C19',
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider alternative therapy (ticagrelor, prasugrel)',
        'Very High Risk': 'Avoid clopidogrel'
    },
    'Simvastatin': {
        'gene': 'SLCO1B1',
        'Low Risk': 'Standard 40mg daily',
        'Moderate Risk': 'Start with 20mg, monitor CK',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid simvastatin'
    },
    'Fluorouracil': {
        'gene': 'DPYD',
        'Low Risk': 'Standard dosing (500mg/m²)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Consider 50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil'
    },
    'Codeine': {
        'gene': 'CYP2D6',
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine, consider tramadol',
        'Very High Risk': 'Use non-opioid alternatives'
    },
    'Tamoxifen': {
        'gene': 'CYP2D6',
        'Low Risk': 'Standard dosing (20mg daily)',
        'Moderate Risk': 'Monitor for reduced efficacy',
        'High Risk': 'Consider aromatase inhibitor',
        'Very High Risk': 'Switch to anastrozole or letrozole'
    },
    'Phenytoin': {
        'gene': 'CYP2C9',
        'Low Risk': 'Standard dosing (300-400mg daily)',
        'Moderate Risk': 'Monitor levels frequently',
        'High Risk': 'Consider 25% dose reduction',
        'Very High Risk': 'Consider alternative anticonvulsant'
    },
    'Atorvastatin': {
        'gene': 'SLCO1B1',
        'Low Risk': 'Standard dosing (10-20mg)',
        'Moderate Risk': 'Start with 10mg',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid atorvastatin'
    },
    'Capecitabine': {
        'gene': 'DPYD',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': '25% dose reduction',
        'High Risk': '50% dose reduction',
        'Very High Risk': 'Avoid capecitabine'
    },
    'Carbamazepine': {
        'gene': 'HLA-B',
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*1502 allele',
        'Very High Risk': 'Avoid carbamazepine'
    },
    'Abacavir': {
        'gene': 'HLA-B',
        'Low Risk': 'Standard dosing (600mg daily)',
        'Moderate Risk': 'Screen for HLA-B*5701',
        'High Risk': 'Screen for HLA-B*5701',
        'Very High Risk': 'Contraindicated if HLA-B*5701 positive'
    },
    'Allopurinol': {
        'gene': 'HLA-B',
        'Low Risk': 'Standard dosing (100-300mg daily)',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*5801',
        'Very High Risk': 'Avoid allopurinol'
    }
}

print(f"  ✓ Loaded {len(drugs_db)} drugs")

# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================
def get_ancestry_description(ancestry):
    descriptions = {
        'AFR': 'African',
        'EUR': 'European', 
        'EAS': 'East Asian',
        'SAS': 'South Asian',
        'AMR': 'Admixed American'
    }
    return descriptions.get(ancestry, ancestry)

# ============================================================
# 4. CREATE DASH APP
# ============================================================
print("\n[3/4] Creating Dash application...")

app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")
server = app.server

app.layout = html.Div([

    # Header
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Integrating Genetics, Environment, and Clinical Guidelines for Equitable Precision Medicine",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '10px'}),
        html.P(f"📊 Analyzing {dataset_size:,} patient records | {len(drugs_db)} drugs | 5 ancestry groups",
               style={'textAlign': 'center', 'color': '#3498db', 'fontSize': '14px'})
    ], style={'marginBottom': '30px'}),

    # Tabs
    dcc.Tabs([
        
        # ========== TAB 1: CLINICAL CALCULATOR ==========
        dcc.Tab(label='📊 Clinical Calculator', children=[
            html.Div([
                html.H3("Patient Risk Assessment Tool", style={'marginTop': '20px'}),
                
                # Information box about metrics
                html.Div([
                    html.H4("📖 Understanding the Metrics", style={'color': '#2c3e50'}),
                    html.Div([
                        html.Div([
                            html.H5("🧬 Genetic Risk Score (0-100)", style={'color': '#27ae60'}),
                            html.Ul([
                                html.Li("🟢 0-33: Normal metabolizer (standard dosing)"),
                                html.Li("🟡 34-66: Intermediate metabolizer (moderate risk)"),
                                html.Li("🔴 67-100: Poor/Ultrarapid metabolizer (high risk)")
                            ])
                        ], style={'width': '45%', 'display': 'inline-block', 
                                 'backgroundColor': '#f0fdf4', 'padding': '15px', 'borderRadius': '10px'}),
                        
                        html.Div([
                            html.H5("🏠 SES Vulnerability Score (0-1)", style={'color': '#e67e22'}),
                            html.Ul([
                                html.Li("Poverty rate (% below federal poverty line)"),
                                html.Li("Unemployment rate"),
                                html.Li("Education level (% without high school diploma)")
                            ])
                        ], style={'width': '45%', 'display': 'inline-block', 
                                 'backgroundColor': '#fff3e0', 'padding': '15px', 'marginLeft': '20px', 
                                 'borderRadius': '10px'})
                    ]),
                    html.Div([
                        html.P("Equity Score = (Genetic Risk × 0.5) + (SES Score × 100 × 0.5)", 
                               style={'textAlign': 'center', 'fontWeight': 'bold'})
                    ])
                ], style={'backgroundColor': '#e8f4f8', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                
                # Inputs
                html.Div([
                    html.Div([
                        html.Label("Patient Ancestry:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='ancestry-input',
                            options=[{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                     for a in sorted(df['ancestry'].unique())],
                            placeholder='Select ancestry...',
                            style={'marginBottom': '15px'}
                        )
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.Label("SES Vulnerability Score (0-1):", style={'fontWeight': 'bold'}),
                        html.Div([
                            html.Span("🟢 Low", style={'color': '#27ae60', 'marginRight': '20px'}),
                            html.Span("🟡 Medium", style={'color': '#f39c12', 'marginRight': '20px'}),
                            html.Span("🟠 High", style={'color': '#e67e22', 'marginRight': '20px'}),
                            html.Span("🔴 Very High", style={'color': '#e74c3c'})
                        ], style={'marginBottom': '5px'}),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.01, value=0.5,
                            marks={i/10: f'{i/10:.1f}' for i in range(0, 11)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'width': '65%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.Label("Genetic Risk Score (0-100):", style={'fontWeight': 'bold'}),
                        html.Div([
                            html.Span("🟢 Normal (0-33)", style={'color': '#27ae60', 'marginRight': '20px'}),
                            html.Span("🟡 Moderate (34-66)", style={'color': '#f39c12', 'marginRight': '20px'}),
                            html.Span("🔴 High (67-100)", style={'color': '#e74c3c'})
                        ], style={'marginBottom': '5px'}),
                        dcc.Slider(
                            id='genetic-slider',
                            min=0, max=100, step=1, value=33,
                            marks={i: str(i) for i in range(0, 101, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'width': '100%', 'padding': '10px', 'marginTop': '20px'})
                ]),
                
                # Risk Warning
                html.Div(id='risk-warning', style={'marginTop': '10px'}),
                
                # Results
                html.Div(id='calculator-results', style={'marginTop': '10px', 'padding': '20px', 
                                                         'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
                
                # Patient Report Button
                html.Div([
                    html.Button("📄 Generate Patient Report", id="generate-report-btn", 
                                style={'backgroundColor': '#3498db', 'color': 'white', 
                                       'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px',
                                       'cursor': 'pointer', 'marginTop': '20px'}),
                    dcc.Download(id="download-report")
                ], style={'textAlign': 'center'})
                
            ], style={'padding': '20px'})
        ]),
        
        # ========== TAB 2: DISPARITY MAP ==========
        dcc.Tab(label='🗺️ Disparity Map', children=[
            html.Div([
                html.H3("Population Health Disparities", style={'marginTop': '20px'}),
                html.P(f"Based on {dataset_size:,} patient records across ancestry groups", 
                       style={'marginBottom': '20px', 'color': '#666'}),
                
                html.Div([
                    html.Label("Filter by Ancestry:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='ancestry-filter',
                        options=[{'label': 'All Groups', 'value': 'All'}] + 
                                [{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                 for a in sorted(df['ancestry'].unique())],
                        value='All',
                        style={'width': '50%', 'marginBottom': '20px'}
                    )
                ]),
                
                dcc.Loading(dcc.Graph(id='equity-distribution')),
                dcc.Loading(dcc.Graph(id='risk-heatmap'))
            ], style={'padding': '20px'})
        ]),
        
        # ========== TAB 3: DRUG GUIDELINES ==========
        dcc.Tab(label='📋 Drug Guidelines', children=[
            html.Div([
                html.H3("Clinical Recommendations", style={'marginTop': '20px'}),
                
                html.Div([
                    html.Label("Search Drugs:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='drug-search',
                        type='text',
                        placeholder='🔍 Search by drug name or gene...',
                        style={'width': '100%', 'padding': '10px', 'marginBottom': '15px', 
                               'borderRadius': '5px', 'border': '1px solid #ddd'}
                    ),
                ]),
                
                html.Div([
                    html.Label("Select Drug:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='drug-select',
                        options=[{'label': f"{drug} ({drugs_db[drug]['gene']})", 'value': drug} 
                                 for drug in drugs_db.keys()],
                        value='Warfarin',
                        style={'width': '100%', 'marginBottom': '20px'}
                    )
                ]),
                
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        # ========== TAB 4: ABOUT ==========
        dcc.Tab(label='ℹ️ About', children=[
            html.Div([
                html.H3("About the Pharmacogenomic Equity Atlas", style={'marginTop': '20px'}),
                html.P("This tool integrates genetic and socioeconomic data to identify patients at risk for adverse drug reactions."),
                
                html.H4("🎯 Purpose", style={'marginTop': '20px'}),
                html.P("The Pharmacogenomic Equity Score (PES) combines genetic risk and social vulnerability to guide personalized therapy."),
                
                html.H4("📊 How to Use", style={'marginTop': '15px'}),
                html.Ol([
                    html.Li("Select patient ancestry"),
                    html.Li("Adjust SES vulnerability based on neighborhood"),
                    html.Li("Adjust genetic risk based on testing results"),
                    html.Li("Review personalized drug recommendations"),
                    html.Li("Generate patient report for documentation")
                ]),
                
                html.H4("💊 Supported Drugs", style={'marginTop': '15px'}),
                html.Div([
                    html.Ul([html.Li(f"{drug} ({drugs_db[drug]['gene']})") 
                            for drug in list(drugs_db.keys())[:6]])
                ], style={'width': '45%', 'display': 'inline-block'}),
                html.Div([
                    html.Ul([html.Li(f"{drug} ({drugs_db[drug]['gene']})") 
                            for drug in list(drugs_db.keys())[6:]])
                ], style={'width': '45%', 'display': 'inline-block'}),
                
                html.H4("🔬 Data Sources", style={'marginTop': '15px'}),
                html.Ul([
                    html.Li("1000 Genomes Project - Population genetics"),
                    html.Li("gnomAD - Variant frequencies"),
                    html.Li("GTEx - Tissue-specific expression"),
                    html.Li("CDC SVI - Socioeconomic vulnerability"),
                    html.Li("PharmGKB/CPIC - Clinical guidelines")
                ]),
                
                html.H4("⚠️ Disclaimer", style={'marginTop': '20px'}),
                html.P("This tool is for educational and research purposes only. All clinical decisions should be made by qualified healthcare providers.")
            ], style={'padding': '20px'})
        ])
    ])
])

# ============================================================
# 5. CALLBACKS
# ============================================================
print("\n[4/4] Defining callbacks...")

# Calculator callback
@app.callback(
    Output('calculator-results', 'children'),
    Output('risk-warning', 'children'),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def update_calculator(ancestry, ses_score, genetic_risk):
    if not ancestry:
        return html.Div("⚠️ Please select ancestry", style={'color': '#e74c3c'}), html.Div()
    
    equity_score = (genetic_risk * 0.5 + (ses_score * 100) * 0.5)
    
    if equity_score < 25:
        risk_category = "Low Risk"
        color = "#27ae60"
        icon = "🟢"
        bg_color = "#f0fdf4"
    elif equity_score < 50:
        risk_category = "Moderate Risk"
        color = "#f39c12"
        icon = "🟡"
        bg_color = "#fef9e7"
    elif equity_score < 75:
        risk_category = "High Risk"
        color = "#e67e22"
        icon = "🟠"
        bg_color = "#fdf2e9"
    else:
        risk_category = "Very High Risk"
        color = "#e74c3c"
        icon = "🔴"
        bg_color = "#fdedec"
    
    # Generate warnings
    warnings_div = []
    if ses_score > 0.8 and genetic_risk > 66:
        warnings_div.append(html.Div([
            html.Span("🔴 HIGH RISK ALERT", style={'color': '#e74c3c', 'fontWeight': 'bold'}),
            html.P("High genetic risk + high SES vulnerability. Consider alternative therapy and enhanced monitoring.")
        ], style={'backgroundColor': '#fdedec', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '10px'}))
    elif genetic_risk > 66:
        warnings_div.append(html.Div([
            html.Span("⚠️ High Genetic Risk", style={'color': '#e67e22', 'fontWeight': 'bold'}),
            html.P("Patient carries multiple risk alleles. Genotype-guided dosing recommended.")
        ], style={'backgroundColor': '#fdf2e9', 'padding': '10px', 'borderRadius': '10px'}))
    elif ses_score > 0.7:
        warnings_div.append(html.Div([
            html.Span("⚠️ High SES Vulnerability", style={'color': '#e67e22', 'fontWeight': 'bold'}),
            html.P("Patient lives in high-vulnerability area. Enhanced monitoring recommended.")
        ], style={'backgroundColor': '#fdf2e9', 'padding': '10px', 'borderRadius': '10px'}))
    
    # Generate recommendations
    recommendations = []
    for drug, info in drugs_db.items():
        rec = info[risk_category]
        recommendations.append(html.Li(f"💊 {drug}: {rec}", style={'marginBottom': '8px'}))
    
    results = html.Div([
        html.H4(f"{icon} {risk_category}", style={'color': color, 'marginBottom': '15px'}),
        html.P(f"🌍 Ancestry: {ancestry} - {get_ancestry_description(ancestry)}"),
        html.P(f"🏠 SES Score: {ses_score:.2f}"),
        html.P(f"🧬 Genetic Risk: {genetic_risk:.0f}"),
        html.H5(f"📊 Equity Score: {equity_score:.1f}", style={'marginTop': '15px', 'color': color}),
        html.H5("Clinical Recommendations:", style={'marginTop': '20px'}),
        html.Ul(recommendations, style={'maxHeight': '300px', 'overflowY': 'auto'})
    ], style={'backgroundColor': bg_color, 'padding': '20px', 'borderRadius': '10px', 'borderLeft': f'5px solid {color}'})
    
    return results, html.Div(warnings_div) if warnings_div else html.Div()

# Disparity callbacks
@app.callback(
    Output('equity-distribution', 'figure'),
    Input('ancestry-filter', 'value')
)
def update_distribution(ancestry_filter):
    if ancestry_filter == 'All':
        plot_df = df
        title = f"Equity Score Distribution by Ancestry (n={len(plot_df):,})"
    else:
        plot_df = df[df['ancestry'] == ancestry_filter]
        title = f"Equity Score Distribution - {ancestry_filter} (n={len(plot_df):,})"
    
    fig = px.histogram(plot_df, x='equity_score', color='ancestry', 
                       nbins=30, title=title,
                       labels={'equity_score': 'Equity Score (0-100)', 'count': 'Number of Patients'},
                       color_discrete_sequence=px.colors.qualitative.Set2)
    fig.add_vline(x=25, line_dash="dash", line_color="green", annotation_text="Low Risk")
    fig.add_vline(x=50, line_dash="dash", line_color="orange", annotation_text="Moderate")
    fig.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="High Risk")
    fig.update_layout(height=500, title_x=0.5)
    return fig

@app.callback(
    Output('risk-heatmap', 'figure'),
    Input('ancestry-filter', 'value')
)
def update_heatmap(ancestry_filter):
    if ancestry_filter == 'All':
        heatmap_df = df
    else:
        heatmap_df = df[df['ancestry'] == ancestry_filter]
    
    heatmap_df = heatmap_df.copy()
    if 'ses_score' in heatmap_df.columns:
        heatmap_df['ses_quartile'] = pd.qcut(heatmap_df['ses_score'], 4, 
                                              labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    else:
        heatmap_df['ses_quartile'] = pd.qcut(heatmap_df['equity_score'], 4, 
                                              labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    
    heatmap_data = heatmap_df.groupby(['ancestry', 'ses_quartile'])['high_risk'].mean().unstack()
    
    fig = px.imshow(heatmap_data, title="High Risk Proportion by Ancestry and SES",
                    color_continuous_scale="RdYlGn_r", aspect="auto", text_auto='.2f')
    fig.update_layout(height=500)
    return fig

# Drug search callback
@app.callback(
    Output('drug-select', 'options'),
    Input('drug-search', 'value')
)
def filter_drugs(search_term):
    if not search_term:
        return [{'label': f"{drug} ({drugs_db[drug]['gene']})", 'value': drug} 
                for drug in drugs_db.keys()]
    
    search_lower = search_term.lower()
    filtered = [drug for drug in drugs_db.keys() 
                if search_lower in drug.lower() 
                or search_lower in drugs_db[drug]['gene'].lower()]
    return [{'label': f"{drug} ({drugs_db[drug]['gene']})", 'value': drug} 
            for drug in filtered]

# Guidelines callback
@app.callback(
    Output('guidelines-table', 'children'),
    Input('drug-select', 'value')
)
def update_guidelines(drug):
    if not drug or drug not in drugs_db:
        return html.Div("Drug not found")
    
    info = drugs_db[drug]
    
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
            html.Td(risk, style={'backgroundColor': risk_color, 'color': 'white', 'fontWeight': 'bold', 'padding': '10px'}),
            html.Td(info[risk], style={'padding': '10px'})
        ]))
    
    return html.Div([
        html.Div([
            html.H3(drug, style={'display': 'inline-block', 'marginRight': '15px'}),
        ], style={'marginBottom': '20px'}),
        html.P(f"Gene: {info['gene']}", style={'fontSize': '16px', 'marginBottom': '20px'}),
        html.Table(rows, style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'}),
        html.P("⚠️ These recommendations are for educational purposes. Always consult a clinical pharmacist.",
               style={'marginTop': '20px', 'fontStyle': 'italic', 'color': '#666'})
    ])

# Patient report callback
@app.callback(
    Output("download-report", "data"),
    Input("generate-report-btn", "n_clicks"),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def generate_report(n_clicks, ancestry, ses_score, genetic_risk):
    if n_clicks is None or not ancestry:
        return None
    
    equity_score = (genetic_risk * 0.5 + (ses_score * 100) * 0.5)
    
    if equity_score < 25:
        risk_level = "Low Risk"
        risk_color = "#27ae60"
    elif equity_score < 50:
        risk_level = "Moderate Risk"
        risk_color = "#f39c12"
    elif equity_score < 75:
        risk_level = "High Risk"
        risk_color = "#e67e22"
    else:
        risk_level = "Very High Risk"
        risk_color = "#e74c3c"
    
    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pharmacogenomic Patient Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
            .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f5f5f5; }}
            .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 Pharmacogenomic Patient Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>Patient Profile</h2>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
                <tr><td>Ancestry</td><td>{ancestry} - {get_ancestry_description(ancestry)}</td></tr>
                <tr><td>SES Vulnerability</td><td>{ses_score:.2f} / 1.00</td></tr>
                <tr><td>Genetic Risk</td><td>{genetic_risk:.0f} / 100</td></tr>
                <tr><td>Equity Score</td><td>{equity_score:.1f} / 100</td></tr>
                <tr><td style='font-weight:bold'>Risk Level</td><td style='color:{risk_color}; font-weight:bold'>{risk_level}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Clinical Recommendations</h2>
            <table>
                <tr><th>Drug</th><th>Gene</th><th>Recommendation</th></tr>
    """
    
    for drug, info in drugs_db.items():
        if equity_score < 25:
            rec = info['Low Risk']
        elif equity_score < 50:
            rec = info['Moderate Risk']
        elif equity_score < 75:
            rec = info['High Risk']
        else:
            rec = info['Very High Risk']
        report_html += f"<tr><td>{drug}</td><td>{info['gene']}</td><td>{rec}</td></tr>"
    
    report_html += f"""
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Pharmacogenomic Equity Atlas | For clinical use only</p>
            <p>Always consult a clinical pharmacist before making treatment decisions.</p>
        </div>
    </body>
    </html>
    """
    
    return dcc.send_bytes(report_html.encode(), f"patient_report_{ancestry}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

# ============================================================
# 6. RUN THE APP
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"\n🌐 Server running at http://localhost:{port}")
    print("📊 Features:")
    print("   • Clinical calculator with continuous sliders")
    print("   • Drug search by name or gene")
    print("   • Risk warnings for high-risk profiles")
    print("   • Patient report generation")
    print("   • Disparity visualizations")
    print("\n💡 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=port, debug=False)
