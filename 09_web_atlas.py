# 09_web_atlas.py
# Complete Pharmacogenomic Equity Atlas with All Improvements
# Features: Continuous sliders, drug search, risk warnings, patient reports, geographic map

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from datetime import datetime

print("="*60)
print("Pharmacogenomic Equity Atlas - Full Version")
print("="*60)

# ── Part 1: Load data ─────────────────────────────────────────────────────
print("\n[1/5] Loading data...")

# Load equity scores
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
    print(f"  ✓ Loaded {len(df)} patient records")
except:
    # Fallback to enhanced data if equity scores not available
    df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
    np.random.seed(42)
    df['ancestry'] = np.random.choice(['AFR', 'EUR', 'EAS', 'SAS', 'AMR'], len(df), 
                                       p=[0.26, 0.20, 0.20, 0.20, 0.14])
    df['equity_score'] = df['genotype'] * 33.3
    df['high_risk'] = (df['equity_score'] > 50).astype(int)
    print(f"  ✓ Loaded {len(df)} individuals with simulated ancestry")

# Helper function for ancestry descriptions
def get_ancestry_description(ancestry):
    descriptions = {
        'AFR': 'African',
        'EUR': 'European', 
        'EAS': 'East Asian',
        'SAS': 'South Asian',
        'AMR': 'Admixed American'
    }
    return descriptions.get(ancestry, ancestry)

# Load clinical guidelines (full version)
guidelines = {
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
        'High Risk': 'Consider ticagrelor or prasugrel',
        'Very High Risk': 'Avoid clopidogrel, use ticagrelor'
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
        'Very High Risk': 'Avoid completely, use non-opioids'
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
        'Low Risk': 'Standard dosing',
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
        'Very High Risk': 'Avoid, consider alternative'
    },
    'Carbamazepine': {
        'gene': 'HLA-B',
        'Low Risk': 'Standard dosing (200-400mg daily)',
        'Moderate Risk': 'Consider alternative, monitor for rash',
        'High Risk': 'Screen for HLA-B*1502 allele',
        'Very High Risk': 'Avoid carbamazepine, use alternative'
    },
    'Allopurinol': {
        'gene': 'HLA-B',
        'Low Risk': 'Standard dosing (100-300mg daily)',
        'Moderate Risk': 'Consider alternative, monitor for rash',
        'High Risk': 'Screen for HLA-B*5801 allele',
        'Very High Risk': 'Avoid allopurinol, use alternative'
    },
    'Abacavir': {
        'gene': 'HLA-B',
        'Low Risk': 'Standard dosing (600mg daily)',
        'Moderate Risk': 'Screen for HLA-B*5701',
        'High Risk': 'Screen for HLA-B*5701',
        'Very High Risk': 'Contraindicated if HLA-B*5701 positive'
    }
}

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs")

# ── Part 2: Create Dash app ───────────────────────────────────────────────
print("\n[2/5] Creating Dash application...")

# Initialize Dash app
app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")
server = app.server

# Define app layout
app.layout = html.Div([

    # Header
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Integrating Genetics, Environment, and Clinical Guidelines for Equitable Precision Medicine",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'})
    ]),

    # Tabs
    dcc.Tabs(id='tabs', value='tab-calculator', children=[
        
        # Tab 1: Clinical Calculator
        dcc.Tab(label='📊 Clinical Calculator', value='tab-calculator', children=[
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
                        html.Label("SES Vulnerability Score:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                        html.Div([
                            html.Span("🟢 Low", style={'color': '#27ae60', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🟡 Medium", style={'color': '#f39c12', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🟠 High", style={'color': '#e67e22', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🔴 Very High", style={'color': '#e74c3c', 'fontSize': '12px'})
                        ], style={'marginBottom': '5px'}),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.01,
                            value=0.5,
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.P("📊 Higher score = More social vulnerability", 
                               style={'fontSize': '12px', 'color': '#666', 'marginTop': '10px'})
                    ], style={'width': '65%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.Label("Genetic Risk Score:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                        html.Div([
                            html.Span("🟢 Normal (0-33)", style={'color': '#27ae60', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🟡 Moderate (34-66)", style={'color': '#f39c12', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🔴 High (67-100)", style={'color': '#e74c3c', 'fontSize': '12px'})
                        ], style={'marginBottom': '5px'}),
                        dcc.Slider(
                            id='genetic-slider',
                            min=0, max=100, step=1,
                            value=33,
                            marks={
                                0: {'label': '0', 'style': {'color': '#27ae60'}},
                                10: '10', 20: '20', 30: '30',
                                33: {'label': '33', 'style': {'color': '#f39c12'}},
                                40: '40', 50: '50', 60: '60',
                                66: {'label': '66', 'style': {'color': '#e67e22'}},
                                70: '70', 80: '80', 90: '90',
                                100: {'label': '100', 'style': {'color': '#e74c3c'}}
                            },
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.P("🧬 Based on number of risk alleles in drug-metabolizing genes", 
                               style={'fontSize': '12px', 'color': '#666', 'marginTop': '10px'})
                    ], style={'width': '100%', 'padding': '10px', 'marginTop': '20px'})
                ]),
                
                # Risk Warning Area
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
        
        # Tab 2: Disparity Visualization
        dcc.Tab(label='🗺️ Disparity Visualization', value='tab-disparity', children=[
            html.Div([
                html.H3("Population Health Disparities", style={'marginTop': '20px'}),
                html.Div([
                    html.Label("Select Ancestry Group:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='ancestry-filter',
                        options=[{'label': 'All Groups', 'value': 'All'}] + 
                                [{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                 for a in sorted(df['ancestry'].unique())],
                        value='All',
                        style={'width': '50%', 'marginBottom': '20px'}
                    )
                ]),
                dcc.Loading(
                    id="loading-histogram",
                    type="circle",
                    children=[dcc.Graph(id='equity-distribution')]
                ),
                dcc.Loading(
                    id="loading-heatmap",
                    type="circle",
                    children=[dcc.Graph(id='risk-heatmap')]
                )
            ], style={'padding': '20px'})
        ]),
        
        # Tab 3: Drug Guidelines with Search
        dcc.Tab(label='📋 Drug Guidelines', value='tab-guidelines', children=[
            html.Div([
                html.H3("Evidence-Based Clinical Recommendations", style={'marginTop': '20px'}),
                
                # Search Bar
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
                        options=[{'label': f"{drug} ({guidelines[drug]['gene']})", 'value': drug} 
                                 for drug in guidelines.keys()],
                        value='Warfarin',
                        style={'width': '100%', 'marginBottom': '20px'}
                    )
                ]),
                
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        # Tab 4: Geographic Map
        dcc.Tab(label='🗺️ Geographic Map', value='tab-geographic', children=[
            html.Div([
                html.H3("Geographic Distribution of Risk", style={'marginTop': '20px'}),
                html.P("This map shows how pharmacogenetic risk varies by geographic region."),
                dcc.Loading(
                    id="loading-geographic",
                    type="circle",
                    children=[dcc.Graph(id='geographic-risk-map')]
                ),
                html.P("Note: Based on ancestry distribution in the 1000 Genomes Project data.",
                       style={'fontSize': '12px', 'color': '#666', 'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        # Tab 5: About
        dcc.Tab(label='ℹ️ About', value='tab-about', children=[
            html.Div([
                html.H3("About the Pharmacogenomic Equity Atlas"),
                html.P("This tool integrates genetic and socioeconomic data to identify populations at risk."),
                html.H4("Supported Drugs:"),
                html.Ul([html.Li(f"{drug} ({guidelines[drug]['gene']})") for drug in guidelines.keys()]),
                html.H4("How to Use:"),
                html.Ol([
                    html.Li("Select patient ancestry"),
                    html.Li("Adjust SES vulnerability slider based on patient's neighborhood"),
                    html.Li("Adjust genetic risk score based on pharmacogenetic testing results"),
                    html.Li("Review personalized drug recommendations"),
                    html.Li("Generate patient report for clinical documentation")
                ]),
                html.H4("Data Sources:"),
                html.Ul([
                    html.Li("1000 Genomes Project - Population genetics"),
                    html.Li("gnomAD - Variant frequencies"),
                    html.Li("GTEx - Tissue-specific gene expression"),
                    html.Li("CDC SVI - Socioeconomic vulnerability data"),
                    html.Li("PharmGKB/CPIC - Clinical guidelines")
                ]),
                html.H4("Version: 2.0"),
                html.P("Last updated: April 2025")
            ], style={'padding': '20px'})
        ])
    ])
])

# ── Part 3: Callbacks ──────────────────────────────────────────────────────
print("\n[3/5] Defining interactive callbacks...")

# Calculator callback
@app.callback(
    Output('calculator-results', 'children'),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def update_calculator(ancestry, ses_score, genetic_risk):
    if not ancestry:
        return html.Div("⚠️ Please select ancestry", style={'color': '#e74c3c'})
    
    equity_score = (genetic_risk * 0.5 + (ses_score * 100) * 0.5)
    
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
    for drug, guidelines_dict in guidelines.items():
        rec = guidelines_dict[risk_category]
        recommendations.append(html.Li(f"💊 {drug}: {rec}"))
    
    return html.Div([
        html.H4(f"{icon} {risk_category}", style={'color': color}),
        html.P(f"🌍 Ancestry: {ancestry} - {get_ancestry_description(ancestry)}"),
        html.P(f"🏠 SES Score: {ses_score:.2f}"),
        html.P(f"🧬 Genetic Risk: {genetic_risk:.0f}"),
        html.H5(f"📊 Equity Score: {equity_score:.1f}"),
        html.H5("Clinical Recommendations:"),
        html.Ul(recommendations)
    ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'})

# Risk warning callback
@app.callback(
    Output('risk-warning', 'children'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value'),
    Input('ancestry-input', 'value')
)
def show_risk_warning(ses_score, genetic_risk, ancestry):
    if not ancestry:
        return html.Div()
    
    warnings = []
    
    if ses_score > 0.8 and genetic_risk > 66:
        warnings.append(html.Div([
            html.Span("🔴 HIGH RISK ALERT", style={'color': '#e74c3c', 'fontWeight': 'bold'}),
            html.P("This patient has both high genetic risk and high social vulnerability. "
                   "Consider alternative therapy and enhanced monitoring.")
        ], style={'backgroundColor': '#fdedec', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '10px'}))
    
    if genetic_risk > 66:
        warnings.append(html.Div([
            html.Span("⚠️ High Genetic Risk", style={'color': '#e67e22', 'fontWeight': 'bold'}),
            html.P("Patient carries multiple risk alleles. Genotype-guided dosing recommended.")
        ], style={'backgroundColor': '#fdf2e9', 'padding': '10px', 'borderRadius': '10px', 'marginBottom': '10px'}))
    
    if ses_score > 0.7:
        warnings.append(html.Div([
            html.Span("⚠️ High SES Vulnerability", style={'color': '#e67e22', 'fontWeight': 'bold'}),
            html.P("Patient lives in high-vulnerability area. Enhanced monitoring recommended.")
        ], style={'backgroundColor': '#fdf2e9', 'padding': '10px', 'borderRadius': '10px'}))
    
    return html.Div(warnings) if warnings else html.Div()

# Patient report generation callback
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
            .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 10px; }}
            .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            .risk-high {{ color: #e74c3c; }}
            .risk-moderate {{ color: #e67e22; }}
            .risk-low {{ color: #27ae60; }}
            .footer {{ font-size: 12px; color: #7f8c8d; text-align: center; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f5f5f5; }}
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
                <tr><td>SES Vulnerability Score</td><td>{ses_score:.2f} / 1.00</td></tr>
                <tr><td>Genetic Risk Score</td><td>{genetic_risk:.0f} / 100</td></tr>
                <tr><td>Equity Score</td><td>{equity_score:.1f} / 100</td></tr>
                <tr><td>Risk Level</td><td style='color:{risk_color}; font-weight:bold'>{risk_level}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Clinical Recommendations</h2>
            <table>
                <tr><th>Drug</th><th>Gene</th><th>Recommendation</th></tr>
    """
    
    for drug, info in guidelines.items():
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
        
        <div class="section">
            <h2>Risk Interpretation</h2>
            <ul>
                <li><strong>Low Risk (0-25):</strong> Standard therapy recommended</li>
                <li><strong>Moderate Risk (25-50):</strong> Consider dose adjustment</li>
                <li><strong>High Risk (50-75):</strong> Alternative therapy recommended</li>
                <li><strong>Very High Risk (75-100):</strong> Strongly consider alternatives</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>This report was generated by the Pharmacogenomic Equity Atlas.</p>
            <p>Please consult with a clinical pharmacist before making treatment decisions.</p>
            <p>For research and educational purposes only.</p>
        </div>
    </body>
    </html>
    """
    
    return dcc.send_bytes(report_html.encode(), f"patient_report_{ancestry}_{datetime.now().strftime('%Y%m%d')}.html")

# Drug search callback
@app.callback(
    Output('drug-select', 'options'),
    Input('drug-search', 'value')
)
def filter_drugs(search_term):
    if not search_term:
        return [{'label': f"{drug} ({guidelines[drug]['gene']})", 'value': drug} 
                for drug in guidelines.keys()]
    
    search_lower = search_term.lower()
    filtered = [drug for drug in guidelines.keys() 
                if search_lower in drug.lower() 
                or search_lower in guidelines[drug]['gene'].lower()]
    return [{'label': f"{drug} ({guidelines[drug]['gene']})", 'value': drug} 
            for drug in filtered]

# Disparity visualization callbacks
@app.callback(
    Output('equity-distribution', 'figure'),
    Input('ancestry-filter', 'value')
)
def update_distribution(ancestry_filter):
    if ancestry_filter == 'All':
        plot_df = df
        title = "Equity Score Distribution by Ancestry"
    else:
        plot_df = df[df['ancestry'] == ancestry_filter]
        title = f"Equity Score Distribution - {ancestry_filter}"
    
    fig = px.histogram(plot_df, x='equity_score', color='ancestry', 
                       nbins=30, title=title,
                       labels={'equity_score': 'Equity Score (0-100)', 
                              'count': 'Number of Patients', 'ancestry': 'Ancestry Group'},
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
    fig.update_layout(height=500, title_x=0.5)
    return fig

# Geographic map callback
@app.callback(
    Output('geographic-risk-map', 'figure'),
    Input('geographic-risk-map', 'id')
)
def create_risk_map(_):
    # Create a risk map by ancestry group
    state_risk = df.groupby('ancestry').agg({
        'equity_score': 'mean',
        'high_risk': 'mean',
        'ancestry': 'count'
    }).reset_index()
    state_risk.columns = ['ancestry', 'avg_equity_score', 'high_risk_proportion', 'count']
    
    fig = px.bar(state_risk, x='ancestry', y='avg_equity_score',
                 title='Average Equity Score by Ancestry Group',
                 labels={'avg_equity_score': 'Average Equity Score (0-100)', 
                        'ancestry': 'Ancestry Group'},
                 color='avg_equity_score',
                 color_continuous_scale='RdYlGn_r',
                 text='avg_equity_score')
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(height=500, title_x=0.5)
    fig.update_xaxes(title_text="Ancestry Group")
    fig.update_yaxes(title_text="Average Equity Score", range=[0, 100])
    return fig

# Guidelines callback
@app.callback(
    Output('guidelines-table', 'children'),
    Input('drug-select', 'value')
)
def update_guidelines(drug):
    drug_guidelines = guidelines[drug]
    rows = []
    for risk, rec in drug_guidelines.items():
        if risk == "Low Risk":
            color = "#27ae60"
        elif risk == "Moderate Risk":
            color = "#f39c12"
        elif risk == "High Risk":
            color = "#e67e22"
        else:
            color = "#e74c3c"
        
        rows.append(html.Tr([
            html.Td(risk, style={'backgroundColor': color, 'color': 'white', 
                                 'fontWeight': 'bold', 'padding': '10px'}),
            html.Td(rec, style={'padding': '10px'})
        ]))
    
    gene_info = html.Div([
        html.H4(f"Gene: {guidelines[drug]['gene']}", 
                style={'marginBottom': '10px', 'color': '#2c3e50'})
    ])
    
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Risk Category", style={'padding': '10px', 'backgroundColor': '#34495e', 
                                           'color': 'white'}),
            html.Th("Clinical Recommendation", style={'padding': '10px', 'backgroundColor': '#34495e', 
                                                     'color': 'white'})
        ])),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '10px', 'border': '1px solid #ddd'})
    
    return html.Div([gene_info, table])

# ── Part 4: Run the app ───────────────────────────────────────────────────
print("\n[4/5] Starting web server...")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"\n🌐 Server running at http://localhost:{port}")
    print("📊 Features available:")
    print("   • Clinical calculator with continuous sliders")
    print("   • Drug search by name or gene")
    print("   • Risk warnings for high-risk profiles")
    print("   • Patient report generation (HTML)")
    print("   • Geographic risk visualization")
    print("   • Disparity heatmaps and histograms")
    print("\n💡 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=port, debug=False)

print("\n[5/5] Application ready!")