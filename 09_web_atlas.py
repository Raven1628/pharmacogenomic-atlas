# 09_web_atlas.py
# Complete Pharmacogenomic Equity Atlas with Continuous Sliders

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

print("="*60)
print("STEP 6: Building Interactive Web Atlas")
print("="*60)

# ── Part 1: Load data ─────────────────────────────────────────────────────
print("\n[1/4] Loading data...")

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
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant (apixaban, rivaroxaban)'
    },
    'Clopidogrel': {
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider ticagrelor or prasugrel',
        'Very High Risk': 'Avoid clopidogrel, use ticagrelor'
    },
    'Simvastatin': {
        'Low Risk': 'Standard 40mg daily',
        'Moderate Risk': 'Start with 20mg, monitor CK',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid simvastatin'
    },
    'Fluorouracil': {
        'Low Risk': 'Standard dosing (500mg/m²)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Consider 50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil'
    },
    'Codeine': {
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine, consider tramadol',
        'Very High Risk': 'Avoid completely, use non-opioids'
    },
    'Tamoxifen': {
        'Low Risk': 'Standard dosing (20mg daily)',
        'Moderate Risk': 'Monitor for reduced efficacy',
        'High Risk': 'Consider aromatase inhibitor',
        'Very High Risk': 'Switch to anastrozole or letrozole'
    },
    'Phenytoin': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor levels frequently',
        'High Risk': 'Consider 25% dose reduction',
        'Very High Risk': 'Consider alternative anticonvulsant'
    },
    'Atorvastatin': {
        'Low Risk': 'Standard dosing (10-20mg)',
        'Moderate Risk': 'Start with 10mg',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid atorvastatin'
    },
    'Capecitabine': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': '25% dose reduction',
        'High Risk': '50% dose reduction',
        'Very High Risk': 'Avoid, consider alternative'
    },
    'Carbamazepine': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Monitor for rash',
        'High Risk': 'Screen for HLA-B*1502',
        'Very High Risk': 'Avoid carbamazepine'
    }
}

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs")

# Create summary statistics by ancestry
ancestry_summary = df.groupby('ancestry').agg({
    'equity_score': ['mean', 'std', 'count'],
    'high_risk': 'mean'
}).round(3)
ancestry_summary.columns = ['mean_equity', 'std_equity', 'n_patients', 'high_risk_prop']
ancestry_summary = ancestry_summary.reset_index()

# ── Part 2: Create Dash app ───────────────────────────────────────────────
print("\n[2/4] Creating Dash application...")

# Initialize Dash app
app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")
server = app.server

# Define app layout - FULL ORIGINAL VERSION WITH CONTINUOUS SLIDERS
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
                
                # Inputs - WITH CONTINUOUS SLIDERS
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
                            min=0, max=1, step=0.01,  # 0.01 step for continuous values
                            value=0.5,
                            marks={
                                0: {'label': '0', 'style': {'color': '#27ae60'}},
                                0.1: '0.1', 0.2: '0.2', 0.3: '0.3', 0.4: '0.4',
                                0.5: {'label': '0.5', 'style': {'color': '#f39c12'}},
                                0.6: '0.6', 0.7: '0.7', 0.8: '0.8', 0.9: '0.9',
                                1: {'label': '1', 'style': {'color': '#e74c3c'}}
                            },
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
                            min=0, max=100, step=1,  # step=1 allows any integer value
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
                
                # Results
                html.Div(id='calculator-results', style={'marginTop': '30px', 'padding': '20px', 
                                                         'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
            ], style={'padding': '20px'})
        ]),
        
        # Tab 2: Disparity Map
        dcc.Tab(label='🗺️ Disparity Visualization', value='tab-map', children=[
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
                dcc.Graph(id='equity-distribution'),
                dcc.Graph(id='risk-heatmap')
            ], style={'padding': '20px'})
        ]),
        
        # Tab 3: Clinical Guidelines
        dcc.Tab(label='📋 Clinical Guidelines', value='tab-guidelines', children=[
            html.Div([
                html.H3("Evidence-Based Clinical Recommendations", style={'marginTop': '20px'}),
                html.Div([
                    html.Label("Select Drug:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='drug-select',
                        options=[{'label': drug, 'value': drug} for drug in guidelines.keys()],
                        value='Warfarin',
                        style={'width': '50%', 'marginBottom': '20px'}
                    )
                ]),
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        # Tab 4: About
        dcc.Tab(label='ℹ️ About', value='tab-about', children=[
            html.Div([
                html.H3("About the Pharmacogenomic Equity Atlas"),
                html.P("This tool integrates genetic and socioeconomic data to identify populations at risk."),
                html.H4("Supported Drugs:"),
                html.Ul([html.Li(drug) for drug in guidelines.keys()])
            ], style={'padding': '20px'})
        ])
    ])
])

# ── Part 3: Callbacks ──────────────────────────────────────────────────────
print("\n[3/4] Defining interactive callbacks...")

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
                       labels={'equity_score': 'Equity Score', 'count': 'Number of Patients'},
                       color_discrete_sequence=px.colors.qualitative.Set2)
    fig.add_vline(x=25, line_dash="dash", line_color="green", annotation_text="Low Risk")
    fig.add_vline(x=50, line_dash="dash", line_color="orange", annotation_text="Moderate")
    fig.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="High Risk")
    fig.update_layout(height=500)
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
    heatmap_df['ses_quartile'] = pd.qcut(heatmap_df['equity_score'], 4, 
                                          labels=['Q1 (Lowest Risk)', 'Q2', 'Q3', 'Q4 (Highest Risk)'])
    
    heatmap_data = heatmap_df.groupby(['ancestry', 'ses_quartile'])['high_risk'].mean().unstack()
    
    fig = px.imshow(heatmap_data, title="High Risk Proportion by Ancestry and Risk Level",
                    color_continuous_scale="RdYlGn_r", aspect="auto", text_auto='.2f')
    fig.update_layout(height=500)
    return fig

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
            html.Td(risk, style={'backgroundColor': color, 'color': 'white', 'fontWeight': 'bold'}),
            html.Td(rec)
        ]))
    
    return html.Table([
        html.Thead(html.Tr([html.Th("Risk Category"), html.Th("Recommendation")])),
        html.Tbody(rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse'})

# ── Part 4: Run the app ───────────────────────────────────────────────────
print("\n[4/4] Starting web server...")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    print(f"\n🌐 Starting server on port {port}")
    print("📊 Open your browser and go to: http://localhost:8050")
    print("🔍 Use the Clinical Calculator to assess patient risk")
    print("🗺️ Explore disparity visualizations")
    print("📋 Review clinical guidelines")
    print("\n💡 TIP: Sliders now support continuous values (0.01 increments)")
    app.run(host='0.0.0.0', port=port, debug=False)
