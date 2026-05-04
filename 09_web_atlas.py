# 09_web_atlas.py
# Step 6 - Interactive Web Atlas (Uses central drug config)

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from drug_config import DRUG_DATABASE, get_drug_list, get_drug_recommendation, get_drug_class

print("="*60)
print("STEP 6: Building Interactive Web Atlas")
print("="*60)

# Load data
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

# Build guidelines dictionary from central config
guidelines = {}
for drug_name in get_drug_list():
    guidelines[drug_name] = {
        'Low Risk': get_drug_recommendation(drug_name, 'low_risk'),
        'Moderate Risk': get_drug_recommendation(drug_name, 'moderate_risk'),
        'High Risk': get_drug_recommendation(drug_name, 'high_risk'),
        'Very High Risk': get_drug_recommendation(drug_name, 'very_high_risk')
    }

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs from central config")

# Initialize Dash app
app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")
server = app.server

# Define app layout
app.layout = html.Div([
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Integrating Genetics, Environment, and Clinical Guidelines for Equitable Precision Medicine",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'})
    ]),
    dcc.Tabs(id='tabs', value='tab-calculator', children=[
        dcc.Tab(label='📊 Clinical Calculator', value='tab-calculator', children=[
            html.Div([
                html.H3("Patient Risk Assessment Tool", style={'marginTop': '20px'}),
                html.Div([
                    html.H4("📖 Understanding the Metrics", style={'color': '#2c3e50', 'marginBottom': '10px'}),
                    html.Div([
                        html.Div([
                            html.H5("🧬 Genetic Risk Score (0-100)", style={'color': '#27ae60'}),
                            html.P("Based on the number of risk alleles in pharmacogenes:"),
                            html.Ul([
                                html.Li("🟢 0-33: Normal metabolizer (standard dosing)"),
                                html.Li("🟡 34-66: Intermediate metabolizer (moderate risk)"),
                                html.Li("🔴 67-100: Poor/Ultrarapid metabolizer (high risk)")
                            ], style={'fontSize': '14px'})
                        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 
                                 'backgroundColor': '#f0fdf4', 'padding': '15px', 'borderRadius': '10px'}),
                        html.Div([
                            html.H5("🏠 SES Vulnerability Score (0-1)", style={'color': '#e67e22'}),
                            html.P("Area-level social vulnerability based on:"),
                            html.Ul([
                                html.Li("Poverty rate (% below federal poverty line)"),
                                html.Li("Unemployment rate"),
                                html.Li("Education level (% without high school diploma)")
                            ], style={'fontSize': '14px'})
                        ], style={'width': '45%', 'display':inline 'inline-block', 'verticalAlign': 'top', 
                                 'backgroundColor': '#fff3e0', 'padding': '15px', 'marginLeft': '20px', 
                                 'borderRadius': '10px'})
                    ]),
                    html.Div([
                        html.H5("🎯 Equity Score Formula:", style={'textAlign': 'center'}),
                        html.P("Equity Score = (Genetic Risk × 0.5) + (SES Score × 100 × 0.5)", 
                               style={'textAlign': 'center', 'fontWeight': 'bold'})
                    ])
                ], style={'backgroundColor': '#e8f4f8', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                html.Div([
                    html.Div([
                        html.Label("Patient Ancestry:", style={'fontWeight': 'bold'}),
                        dcc.Dropdown(
                            id='ancestry-input',
                            options=[{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                     for a in sorted(df['ancestry'].unique())],
                            placeholder='Select ancestry...'
                        )
                    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
                    html.Div([
                        html.Label("SES Vulnerability Score:", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.05,
                            value=0.5,
                            marks={i/10: f'{i/10:.1f}' for i in range(0, 11)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'width': '65%', 'display': 'inline-block', 'padding': '10px'}),
                    html.Div([
                        html.Label("Genetic Risk Score:", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='genetic-slider',
                            min=0, max=100, step=10,
                            value=33,
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'width': '100%', 'padding': '10px', 'marginTop': '20px'})
                ]),
                html.Div(id='calculator-results', style={'marginTop': '30px', 'padding': '20px', 
                                                         'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='🗺️ Disparity Visualization', value='tab-map', children=[
            html.Div([
                html.H3("Population Health Disparities", style={'marginTop': '20px'}),
                html.Div([
                    html.Label("Select Ancestry Group:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='ancestry-filter',
                        options=[{'label': 'All Groups', 'value': 'All'}] + 
                                [{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} for a in sorted(df['ancestry'].unique())],
                        value='All'
                    )
                ]),
                dcc.Graph(id='equity-distribution'),
                dcc.Graph(id='risk-heatmap')
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='📋 Clinical Guidelines', value='tab-guidelines', children=[
            html.Div([
                html.H3("Evidence-Based Clinical Recommendations", style={'marginTop': '20px'}),
                html.Div([
                    html.Label("Select Drug:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='drug-select',
                        options=[{'label': drug, 'value': drug} for drug in guidelines.keys()],
                        value='Warfarin'
                    )
                ]),
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        dcc.Tab(label='ℹ️ About', value='tab-about', children=[
            html.Div([
                html.H3("About the Pharmacogenomic Equity Atlas", style={'marginTop': '20px'}),
                html.P("This tool integrates genetic and socioeconomic data to identify populations at risk."),
                html.H4("Data Sources:"),
                html.Ul([
                    html.Li("1000 Genomes Project - Population genetics"),
                    html.Li("gnomAD - Variant frequencies"),
                    html.Li("GTEx - Tissue-specific gene expression"),
                    html.Li("CDC SVI - Socioeconomic vulnerability data")
                ])
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
def update_calculator(ancestry, ses_score, genetic_risk):
    if not ancestry:
        return html.Div("⚠️ Please select ancestry", style={'textAlign': 'center', 'color': '#e74c3c'})
    
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
    for drug in guidelines.keys():
        rec = guidelines[drug][risk_category]
        recommendations.append(html.Li(f"💊 {drug}: {rec}"))
    
    return html.Div([
        html.H4(f"{icon} Risk: {risk_category}", style={'color': color}),
        html.Div([
            html.P(f"🌍 Ancestry: {ancestry}"),
            html.P(f"🏠 SES Score: {ses_score:.2f}"),
            html.P(f"🧬 Genetic Risk: {genetic_risk:.0f}"),
            html.H5(f"📊 Equity Score: {equity_score:.1f}")
        ]),
        html.H5("Recommendations:"),
        html.Ul(recommendations)
    ])

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
    
    fig = px.histogram(plot_df, x='equity_score', color='ancestry', nbins=30, title=title)
    fig.add_vline(x=25, line_dash="dash", line_color="green")
    fig.add_vline(x=50, line_dash="dash", line_color="orange")
    fig.add_vline(x=75, line_dash="dash", line_color="red")
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
    heatmap_df['ses_quartile'] = pd.qcut(heatmap_df['ses_score'], 4, 
                                          labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    heatmap_data = heatmap_df.groupby(['ancestry', 'ses_quartile'])['high_risk'].mean().unstack()
    
    fig = px.imshow(heatmap_data, title="High Risk Proportion by Ancestry and SES",
                    color_continuous_scale="RdYlGn_r", aspect="auto", text_auto='.2f')
    return fig

@app.callback(
    Output('guidelines-table', 'children'),
    Input('drug-select', 'value')
)
def update_guidelines(drug):
    drug_guidelines = guidelines[drug]
    rows = []
    for risk, rec in drug_guidelines.items():
        rows.append(html.Tr([html.Td(risk), html.Td(rec)]))
    return html.Table(rows, style={'width': '100%', 'border': '1px solid #ddd'})

if __name__ == '__main__':
    print("\n🌐 Starting server at http://127.0.0.1:8050")
    app.run(debug=False, host='0.0.0.0', port=8050)
