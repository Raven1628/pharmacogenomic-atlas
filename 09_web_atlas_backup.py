# 09_web_atlas.py
# Step 6 - Interactive Web Atlas for Pharmacogenomic Equity Score
# WITH LEGENDS AND METRICS EXPLANATIONS

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

# Load clinical guidelines
guidelines = {
    'Warfarin': {
        'Low Risk': 'Standard dosing (5mg daily)',
        'Moderate Risk': 'Consider reduced initial dose (3-4mg)',
        'High Risk': 'Genotype-guided dosing recommended',
        'Very High Risk': 'Alternative anticoagulant (apixaban, rivaroxaban)'
    },
    'Clopidogrel': {
        'Low Risk': 'Standard therapy (75mg daily)',
        'Moderate Risk': 'Monitor platelet function, consider dose adjustment',
        'High Risk': 'Consider alternative antiplatelet (ticagrelor, prasugrel)',
        'Very High Risk': 'Avoid clopidogrel, use ticagrelor 90mg twice daily'
    },
    'Simvastatin': {
        'Low Risk': 'Standard 40mg daily',
        'Moderate Risk': 'Start with 20mg, monitor CK levels',
        'High Risk': 'Use pravastatin or rosuvastatin 10mg',
        'Very High Risk': 'Avoid simvastatin, use alternative statin'
    },
    'Fluorouracil': {
        'Low Risk': 'Standard dosing (500mg/m²)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Consider 50% dose reduction with monitoring',
        'Very High Risk': 'Avoid fluorouracil, consider alternative (capecitabine with dose adjustment)'
    },
        'Codeine': {
        'Low Risk': 'Standard dosing (30-60mg)',
        'Moderate Risk': 'Consider 25% dose reduction',
        'High Risk': 'Avoid codeine, consider tramadol',
        'Very High Risk': 'Avoid completely, use non-opioid alternatives'
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
server = app.server  # REQUIRED for deployment
server = app.server  # REQUIRED for deployment

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
                    html.H4("📖 Understanding the Metrics", style={'color': '#2c3e50', 'marginBottom': '10px'}),
                    html.Div([
                        html.Div([
                            html.H5("🧬 Genetic Risk Score (0-100)", style={'color': '#27ae60'}),
                            html.P("Based on the number of risk alleles in pharmacogenes (CYP2D6, CYP2C9, CYP2C19, SLCO1B1, DPYD):"),
                            html.Ul([
                                html.Li("🟢 0-33: Normal metabolizer (standard dosing, average risk)"),
                                html.Li("🟡 34-66: Intermediate metabolizer (moderate risk, consider dose adjustment)"),
                                html.Li("🔴 67-100: Poor/Ultrarapid metabolizer (high risk, alternative therapy recommended)")
                            ], style={'fontSize': '14px'})
                        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 
                                 'backgroundColor': '#f0fdf4', 'padding': '15px', 'borderRadius': '10px'}),
                        
                        html.Div([
                            html.H5("🏠 SES Vulnerability Score (0-1)", style={'color': '#e67e22'}),
                            html.P("Area-level social vulnerability based on CDC data:"),
                            html.Ul([
                                html.Li("Poverty rate (% below federal poverty line)"),
                                html.Li("Unemployment rate"),
                                html.Li("Education level (% without high school diploma)"),
                                html.Li("Housing burden and transportation access")
                            ], style={'fontSize': '14px'})
                        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 
                                 'backgroundColor': '#fff3e0', 'padding': '15px', 'marginLeft': '20px', 
                                 'borderRadius': '10px'})
                    ]),
                    
                    html.Div([
                        html.H5("🎯 Equity Score Formula:", 
                               style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '15px'}),
                        html.P("Equity Score = (Genetic Risk × 0.5) + (SES Score × 100 × 0.5)", 
                               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'fontWeight': 'bold'}),
                        html.P("Higher equity score = Higher risk of adverse drug reaction", 
                               style={'textAlign': 'center', 'color': '#e74c3c', 'fontSize': '14px'})
                    ])
                ], style={'backgroundColor': '#e8f4f8', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                
                # Inputs
                html.Div([
                    html.Div([
                        html.Label("Patient Ancestry:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                        dcc.Dropdown(
                            id='ancestry-input',
                            options=[{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                     for a in sorted(df['ancestry'].unique())],
                            placeholder='Select ancestry...',
                            style={'marginBottom': '15px'}
                        ),
                        html.P("👥 Ancestry affects the frequency of genetic variants", 
                               style={'fontSize': '12px', 'color': '#666', 'marginTop': '-10px', 'marginBottom': '15px'})
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
                    
                    html.Div([
                        html.Label("SES Vulnerability Score:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                        html.Div([
                            html.Span("🟢 Low Vulnerability", style={'color': '#27ae60', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🟡 Medium", style={'color': '#f39c12', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🟠 High", style={'color': '#e67e22', 'fontSize': '12px', 'marginRight': '20px'}),
                            html.Span("🔴 Very High", style={'color': '#e74c3c', 'fontSize': '12px'})
                        ], style={'marginBottom': '5px'}),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.05,
                            value=0.5,
                            marks={
                                0: {'label': '0 (Best)', 'style': {'color': '#27ae60'}},
                                0.25: '0.25',
                                0.5: {'label': '0.5 (Avg)', 'style': {'color': '#f39c12'}},
                                0.75: '0.75',
                                1: {'label': '1 (Worst)', 'style': {'color': '#e74c3c'}}
                            },
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.P("📊 Higher score = More social vulnerability (poverty, unemployment, low education)", 
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
                            min=0, max=100, step=10,
                            value=33,
                            marks={
                                0: {'label': '0 (Best)', 'style': {'color': '#27ae60'}},
                                33: {'label': '33 (1 alt)', 'style': {'color': '#f39c12'}},
                                66: {'label': '66 (2 alt)', 'style': {'color': '#e67e22'}},
                                100: {'label': '100 (2 alt+)', 'style': {'color': '#e74c3c'}}
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
                    html.P("📊 This visualization shows how genetic risk and SES vulnerability combine across different ancestry groups.", 
                           style={'backgroundColor': '#e8f4f8', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '20px'})
                ]),
                
                # Filters
                html.Div([
                    html.Label("Select Ancestry Group:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='ancestry-filter',
                        options=[{'label': 'All Groups', 'value': 'All'}] + 
                                [{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} for a in sorted(df['ancestry'].unique())],
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
                    html.P("📚 Based on CPIC (Clinical Pharmacogenetics Implementation Consortium) and FDA guidelines", 
                           style={'backgroundColor': '#e8f4f8', 'padding': '15px', 'borderRadius': '10px', 'marginBottom': '20px'})
                ]),
                
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
                for adverse drug reactions and therapeutic failure. 
                """),
                
                html.H4("🎯 Purpose"),
                html.P("""
                The Pharmacogenomic Equity Score (PES) combines genetic risk and social vulnerability 
                to guide personalized drug therapy and address health disparities.
                """),
                
                html.H4("📊 How to Use This Tool"),
                html.Ul([
                    html.Li("Select patient ancestry from the dropdown"),
                    html.Li("Adjust SES vulnerability slider based on patient's neighborhood"),
                    html.Li("Adjust genetic risk score based on pharmacogenetic testing results"),
                    html.Li("Review personalized drug recommendations for Warfarin, Clopidogrel, Simvastatin, and Fluorouracil")
                ]),
                
                html.H4("🔬 Data Sources"),
                html.Ul([
                    html.Li("1000 Genomes Project - Population genetics"),
                    html.Li("gnomAD - Variant frequencies"),
                    html.Li("GTEx - Tissue-specific gene expression"),
                    html.Li("CDC SVI - Socioeconomic vulnerability data"),
                    html.Li("PharmGKB/CPIC - Clinical guidelines")
                ]),
                
                html.H4("📈 Equity Score Interpretation"),
                html.Ul([
                    html.Li("🟢 0-25: Low Risk - Standard clinical care"),
                    html.Li("🟡 25-50: Moderate Risk - Increased monitoring"),
                    html.Li("🟠 50-75: High Risk - Consider alternative therapy"),
                    html.Li("🔴 75-100: Very High Risk - Strongly consider alternatives")
                ]),
                
                html.H4("⚠️ Disclaimer"),
                html.P("""
                This tool is for educational and research purposes only. 
                All clinical decisions should be made by qualified healthcare providers 
                    based on complete patient evaluation.
                """),
                
                html.H4("📧 Contact"),
                html.P("For questions or collaborations, please contact the research team.")
            ], style={'padding': '20px'})
        ])
    ])
])

# Add server for deployment
server = app.server

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
        return html.Div("⚠️ Please select ancestry to see recommendations", 
                       style={'textAlign': 'center', 'color': '#e74c3c', 'padding': '20px'})
    
    # Calculate equity score
    equity_score = (genetic_risk * 0.5 + (ses_score * 100) * 0.5)
    
    # Determine risk category
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
    
    # Get recommendations
    recommendations = []
    for drug, guidelines_dict in guidelines.items():
        rec = guidelines_dict[risk_category]
        recommendations.append(html.Li(f"💊 {drug}: {rec}", style={'marginBottom': '10px'}))
    
    # Create result display
    return html.Div([
        html.H4(f"{icon} Patient Risk Assessment: {risk_category}", 
                style={'color': color, 'textAlign': 'center'}),
        html.Hr(),
        html.Div([
            html.Div([
                html.P("📋 Patient Profile", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P(f"🌍 Ancestry: {ancestry} - {get_ancestry_description(ancestry)}", style={'fontSize': '14px'}),
                html.P(f"🏠 SES Score: {ses_score:.2f} / 1.0", style={'fontSize': '14px'}),
                html.P(f"🧬 Genetic Risk: {genetic_risk:.0f} / 100", style={'fontSize': '14px'}),
                html.H5(f"📊 Equity Score: {equity_score:.1f}", 
                       style={'color': color, 'fontSize': '20px', 'marginTop': '15px'})
            ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            html.Div([
                html.P("💊 Clinical Recommendations", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.Ul(recommendations, style={'marginTop': '0px'})
            ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '20px'})
        ]),
        html.Hr(),
        html.P("⚠️ These recommendations are for educational purposes. Always consult a clinical pharmacist.",
               style={'marginTop': '15px', 'fontStyle': 'italic', 'color': '#7f8c8d', 'fontSize': '12px', 'textAlign': 'center'})
    ], style={'backgroundColor': bg_color, 'padding': '20px', 'borderRadius': '10px', 'borderLeft': f'5px solid {color}'})

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
        title = f"Equity Score Distribution - {ancestry_filter} ({get_ancestry_description(ancestry_filter)})"
    
    fig = px.histogram(plot_df, x='equity_score', color='ancestry', 
                       nbins=30, title=title,
                       labels={'equity_score': 'Pharmacogenomic Equity Score (0-100)', 
                              'count': 'Number of Patients', 'ancestry': 'Ancestry Group'},
                       color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=500, 
                      xaxis_title="Equity Score (higher = higher risk)",
                      yaxis_title="Number of Patients")
    fig.add_vline(x=25, line_dash="dash", line_color="green", annotation_text="Low Risk")
    fig.add_vline(x=50, line_dash="dash", line_color="orange", annotation_text="Moderate")
    fig.add_vline(x=75, line_dash="dash", line_color="red", annotation_text="High Risk")
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
                                          labels=['Q1 (Lowest Vulnerability)', 'Q2', 'Q3', 'Q4 (Highest Vulnerability)'])
    
    # Calculate risk by ancestry and SES
    heatmap_data = heatmap_df.groupby(['ancestry', 'ses_quartile'])['high_risk'].mean().unstack()
    
    fig = px.imshow(heatmap_data, 
                    title="High Risk Proportion by Ancestry and SES Vulnerability",
                    labels=dict(x="SES Vulnerability Quartile", y="Ancestry", color="Proportion High Risk"),
                    color_continuous_scale="RdYlGn_r",
                    aspect="auto",
                    text_auto='.2f')
    fig.update_layout(height=500)
    fig.update_xaxes(side="bottom")
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
            html.Td(risk, style={'backgroundColor': color, 'color': 'white', 'fontWeight': 'bold', 'padding': '10px'}),
            html.Td(rec, style={'padding': '10px'})
        ]))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Risk Category", style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'}),
            html.Th("Clinical Recommendation", style={'padding': '10px', 'backgroundColor': '#34495e', 'color': 'white'})
        ])),
        html.Tbody(table_rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '20px', 'border': '1px solid #ddd'})

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
    print("\n💡 TIP: Hover over any graph for more information")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    app.run(debug=False, host='0.0.0.0', port=8050)