# 09_web_atlas.py
# Step 6 - Interactive Web Atlas for Pharmacogenomic Equity Score

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from flask import Flask

print("="*60)
print("STEP 6: Building Interactive Web Atlas")
print("="*60)

# ── Part 1: Load data ─────────────────────────────────────────────────────
print("\n[1/4] Loading data...")

# Load equity scores
df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
print(f"  ✓ Loaded {len(df)} patient records")

# Load clinical guidelines
guidelines = {
    'Warfarin': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Consider reduced initial dose',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant strongly consider'
    },
    'Clopidogrel': {
        'Low Risk': 'Standard therapy',
        'Moderate Risk': 'Monitor platelet function',
        'High Risk': 'Consider alternative antiplatelet',
        'Very High Risk': 'Avoid clopidogrel, use ticagrelor'
    },
    'Simvastatin': {
        'Low Risk': 'Standard 40mg',
        'Moderate Risk': 'Start with 20mg',
        'High Risk': 'Use pravastatin or rosuvastatin',
        'Very High Risk': 'Avoid simvastatin, use alternative statin'
    },
    'Fluorouracil': {
        'Low Risk': 'Standard dosing',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Consider 50% dose reduction',
        'Very High Risk': 'Avoid fluorouracil, consider alternative'
    }
}

# Create summary statistics by ancestry
ancestry_summary = df.groupby('ancestry').agg({
    'equity_score': ['mean', 'std', 'count'],
    'high_risk': 'mean'
}).round(3)
ancestry_summary.columns = ['mean_equity', 'std_equity', 'n_patients', 'high_risk_prop']
ancestry_summary = ancestry_summary.reset_index()

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs")

# ── Part 2: Create Dash app ───────────────────────────────────────────────
print("\n[2/4] Creating Dash application...")

# Initialize Dash app
app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")

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
                
                # Inputs
                html.Div([
                    html.Div([
                        html.Label("Patient Ancestry:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='ancestry-input',
                            options=[{'label': a, 'value': a} for a in df['ancestry'].unique()],
                            placeholder='Select ancestry...',
                            style={'marginBottom': '15px'}
                        ),
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.Label("SES Vulnerability Score (0-1):", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.05,
                            value=0.5,
                            marks={i/10: f'{i/10:.1f}' for i in range(0, 11)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                    ], style={'width': '65%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.Label("Genetic Risk Score (0-100):", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='genetic-slider',
                            min=0, max=100, step=10,
                            value=33,
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
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
                
                # Filters
                html.Div([
                    html.Label("Select Ancestry Group:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='ancestry-filter',
                        options=[{'label': 'All', 'value': 'All'}] + 
                                [{'label': a, 'value': a} for a in df['ancestry'].unique()],
                        value='All',
                        style={'width': '50%', 'marginBottom': '20px'}
                    )
                ]),
                
                # Graphs
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
                html.H3("About the Pharmacogenomic Equity Atlas", style={'marginTop': '20px'}),
                html.P("""
                This tool integrates genetic and socioeconomic data to identify populations at risk 
                for adverse drug reactions and therapeutic failure. The Pharmacogenomic Equity Score (PES) 
                combines:
                """),
                html.Ul([
                    html.Li("Genetic risk based on pharmacogene variants"),
                    html.Li("Socioeconomic vulnerability (poverty, education, unemployment)"),
                    html.Li("Ancestry-specific population genetics")
                ]),
                html.H4("Clinical Applications:"),
                html.Ul([
                    html.Li("Personalize drug selection and dosing"),
                    html.Li("Identify patients needing enhanced monitoring"),
                    html.Li("Address health disparities in precision medicine"),
                    html.Li("Guide insurance and policy decisions")
                ]),
                html.H4("Data Sources:"),
                html.Ul([
                    html.Li("1000 Genomes Project - Population genetics"),
                    html.Li("gnomAD - Variant frequencies"),
                    html.Li("GTEx - Tissue expression"),
                    html.Li("CDC SVI - Socioeconomic data"),
                    html.Li("PharmGKB - Clinical guidelines")
                ]),
                html.H4("Contact:"),
                html.P("For clinical implementation questions, please contact the research team.")
            ], style={'padding': '20px'})
        ])
    ])
])

# ── Part 3: Define callbacks ──────────────────────────────────────────────
print("\n[3/4] Defining interactive callbacks...")

# Calculator callback
@app.callback(
    Output('calculator-results', 'children'),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def update_calculator(ancestry, ses_score, genetic_risk):
    if not ancestry:
        return html.Div("Please select ancestry to see recommendations", 
                       style={'textAlign': 'center', 'color': '#e74c3c'})
    
    # Calculate equity score
    equity_score = (genetic_risk * 0.5 + (ses_score * 100) * 0.5)
    
    # Determine risk category
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
    
    # Get recommendations
    recommendations = []
    for drug, guidelines_dict in guidelines.items():
        rec = guidelines_dict[risk_category]
        recommendations.append(html.Li(f"💊 {drug}: {rec}"))
    
    # Create result display
    return html.Div([
        html.H4(f"{icon} Patient Risk Assessment", style={'color': color}),
        html.Div([
            html.P(f"Ancestry: {ancestry}", style={'fontSize': '16px'}),
            html.P(f"SES Score: {ses_score:.2f}", style={'fontSize': '16px'}),
            html.P(f"Genetic Risk: {genetic_risk:.0f}", style={'fontSize': '16px'}),
            html.H5(f"Equity Score: {equity_score:.1f}", style={'color': color, 'fontSize': '20px'}),
            html.H5(f"Risk Category: {risk_category}", style={'color': color})
        ]),
        html.H5("Clinical Recommendations:", style={'marginTop': '20px'}),
        html.Ul(recommendations),
        html.P("⚠️ These recommendations should be reviewed by a clinical pharmacist.", 
               style={'marginTop': '20px', 'fontStyle': 'italic', 'color': '#7f8c8d'})
    ])

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
                       labels={'equity_score': 'Pharmacogenomic Equity Score', 
                              'count': 'Number of Patients'},
                       color_discrete_sequence=px.colors.qualitative.Set2)
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
    
    # Create SES quartiles
    heatmap_df = heatmap_df.copy()
    heatmap_df['ses_quartile'] = pd.qcut(heatmap_df['ses_score'], 4, 
                                          labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    
    # Calculate risk by ancestry and SES
    heatmap_data = heatmap_df.groupby(['ancestry', 'ses_quartile'])['high_risk'].mean().unstack()
    
    fig = px.imshow(heatmap_data, 
                    title="High Risk Proportion by Ancestry and SES",
                    labels=dict(x="SES Quartile", y="Ancestry", color="Proportion High Risk"),
                    color_continuous_scale="RdYlGn_r",
                    aspect="auto")
    fig.update_layout(height=400)
    return fig

# Guidelines callback
@app.callback(
    Output('guidelines-table', 'children'),
    Input('drug-select', 'value')
)
def update_guidelines(drug):
    guidelines_dict = guidelines[drug]
    
    table_rows = []
    for risk, rec in guidelines_dict.items():
        if risk == "Low Risk":
            color = "#27ae60"
        elif risk == "Moderate Risk":
            color = "#f39c12"
        elif risk == "High Risk":
            color = "#e67e22"
        else:
            color = "#e74c3c"
        
        table_rows.append(html.Tr([
            html.Td(risk, style={'backgroundColor': color, 'color': 'white', 'fontWeight': 'bold'}),
            html.Td(rec, style={'padding': '10px'})
        ]))
    
    return html.Table([
        html.Thead(html.Tr([html.Th("Risk Category"), html.Th("Recommendation")])),
        html.Tbody(table_rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '20px'})

# ── Part 4: Run the app ───────────────────────────────────────────────────
print("\n[4/4] Starting web server...")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("✓ WEB ATLAS BUILD COMPLETE!")
    print("="*60)
    print("\n🌐 Starting Dash server...")
    print("📊 Open your browser and go to: http://127.0.0.1:8050")
    print("🔍 Use the Clinical Calculator to assess patient risk")
    print("🗺️ Explore disparity visualizations")
    print("📋 Review clinical guidelines")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=8050)  # Changed from run_server to runserver = app.server
server = app.server
