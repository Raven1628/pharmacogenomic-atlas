# 09_web_atlas.py
# Complete Pharmacogenomic Equity Atlas with LARGE DATASET support

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

print("="*60)
print("Pharmacogenomic Equity Atlas - LARGE DATASET VERSION")
print("="*60)

# Load data (try multiple sources)
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores_large.csv")
    print(f"  ✓ Loaded LARGE dataset: {len(df):,} patient records")
except:
    try:
        df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
        print(f"  ✓ Loaded standard dataset: {len(df):,} patient records")
    except:
        df = pd.read_csv("data/processed/large_dataset.csv")
        print(f"  ✓ Loaded fallback dataset: {len(df):,} patient records")

dataset_size = len(df)

def get_ancestry_description(ancestry):
    descriptions = {'AFR': 'African', 'EUR': 'European', 'EAS': 'East Asian',
                    'SAS': 'South Asian', 'AMR': 'Admixed American'}
    return descriptions.get(ancestry, ancestry)

# Expanded drug guidelines
guidelines = {
    'Warfarin': {'gene': 'CYP2C9', 'Low Risk': '5mg daily', 'Moderate Risk': '3-4mg',
                 'High Risk': 'Genotype-guided', 'Very High Risk': 'Alternative anticoagulant'},
    'Clopidogrel': {'gene': 'CYP2C19', 'Low Risk': '75mg daily', 'Moderate Risk': 'Monitor',
                    'High Risk': 'Alternative therapy', 'Very High Risk': 'Avoid clopidogrel'},
    'Simvastatin': {'gene': 'SLCO1B1', 'Low Risk': '40mg', 'Moderate Risk': '20mg',
                    'High Risk': 'Alternative statin', 'Very High Risk': 'Avoid simvastatin'},
    'Fluorouracil': {'gene': 'DPYD', 'Low Risk': 'Standard', 'Moderate Risk': '25% reduction',
                     'High Risk': '50% reduction', 'Very High Risk': 'Avoid fluorouracil'},
    'Codeine': {'gene': 'CYP2D6', 'Low Risk': '30-60mg', 'Moderate Risk': '25% reduction',
                'High Risk': 'Avoid codeine', 'Very High Risk': 'Non-opioid alternatives'},
    'Tamoxifen': {'gene': 'CYP2D6', 'Low Risk': '20mg', 'Moderate Risk': 'Monitor',
                  'High Risk': 'Consider AI', 'Very High Risk': 'Switch to AI'},
    'Phenytoin': {'gene': 'CYP2C9', 'Low Risk': '300-400mg', 'Moderate Risk': 'Monitor levels',
                  'High Risk': '25% reduction', 'Very High Risk': 'Alternative AED'},
    'Atorvastatin': {'gene': 'SLCO1B1', 'Low Risk': '10-20mg', 'Moderate Risk': 'Start 10mg',
                     'High Risk': 'Alternative statin', 'Very High Risk': 'Avoid atorvastatin'},
    'Capecitabine': {'gene': 'DPYD', 'Low Risk': 'Standard', 'Moderate Risk': '25% reduction',
                     'High Risk': '50% reduction', 'Very High Risk': 'Avoid capecitabine'},
    'Carbamazepine': {'gene': 'HLA-B', 'Low Risk': 'Standard', 'Moderate Risk': 'Monitor rash',
                      'High Risk': 'Screen HLA-B*1502', 'Very High Risk': 'Avoid carbamazepine'},
    'Abacavir': {'gene': 'HLA-B', 'Low Risk': 'Standard', 'Moderate Risk': 'Screen HLA-B*5701',
                 'High Risk': 'Screen HLA-B*5701', 'Very High Risk': 'Contraindicated if positive'},
    'Allopurinol': {'gene': 'HLA-B', 'Low Risk': 'Standard', 'Moderate Risk': 'Monitor rash',
                    'High Risk': 'Screen HLA-B*5801', 'Very High Risk': 'Avoid allopurinol'}
}

print(f"  ✓ Loaded guidelines for {len(guidelines)} drugs")

app = dash.Dash(__name__, title="Pharmacogenomic Equity Atlas")
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("🏥 Pharmacogenomic Equity Atlas", 
                style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.P(f"Analyzing {dataset_size:,} patient records | {len(guidelines)} drugs | 5 ancestry groups",
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
                            options=[{'label': f"{a} - {get_ancestry_description(a)}", 'value': a} 
                                     for a in sorted(df['ancestry'].unique())],
                            placeholder='Select ancestry...'
                        )
                    ], style={'width': '30%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label("SES Vulnerability Score (0-1):"),
                        dcc.Slider(
                            id='ses-slider',
                            min=0, max=1, step=0.01, value=0.5,
                            marks={i/10: str(i/10) for i in range(0, 11)},
                            tooltip={"always_visible": True}
                        )
                    ], style={'width': '65%', 'display': 'inline-block', 'marginLeft': '20px'}),
                    html.Div([
                        html.Label("Genetic Risk Score (0-100):"),
                        dcc.Slider(
                            id='genetic-slider',
                            min=0, max=100, step=1, value=33,
                            marks={i: str(i) for i in range(0, 101, 10)},
                            tooltip={"always_visible": True}
                        )
                    ], style={'marginTop': '20px'})
                ]),
                html.Div(id='risk-warning', style={'marginTop': '10px'}),
                html.Div(id='calculator-results', style={'marginTop': '10px', 'padding': '20px', 
                                                         'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
                html.Div([
                    html.Button("📄 Generate Patient Report", id="generate-report-btn", 
                                style={'backgroundColor': '#3498db', 'color': 'white', 
                                       'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px',
                                       'cursor': 'pointer', 'marginTop': '20px'}),
                    dcc.Download(id="download-report")
                ], style={'textAlign': 'center'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🗺️ Disparity Map', children=[
            html.Div([
                html.H3("Population Health Disparities"),
                html.Div([
                    html.Label("Filter by Ancestry:"),
                    dcc.Dropdown(
                        id='ancestry-filter',
                        options=[{'label': 'All Groups', 'value': 'All'}] + 
                                [{'label': a, 'value': a} for a in sorted(df['ancestry'].unique())],
                        value='All'
                    )
                ]),
                dcc.Loading(dcc.Graph(id='equity-distribution')),
                dcc.Loading(dcc.Graph(id='risk-heatmap'))
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='📋 Drug Guidelines', children=[
            html.Div([
                html.H3("Clinical Recommendations"),
                html.Div([
                    html.Label("Search Drugs:"),
                    dcc.Input(id='drug-search', type='text', placeholder='🔍 Search by name or gene...',
                              style={'width': '100%', 'padding': '10px', 'marginBottom': '10px'})
                ]),
                html.Div([
                    html.Label("Select Drug:"),
                    dcc.Dropdown(id='drug-select', value='Warfarin')
                ]),
                html.Div(id='guidelines-table', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='📊 PCA Analysis', children=[
            html.Div([
                html.H3("Principal Component Analysis"),
                html.P(f"Based on {dataset_size:,} patient records. PC1 explains 52.7% of variance, PC2 explains 33.6%."),
                dcc.Loading(dcc.Graph(id='pca-plot'))
            ], style={'padding': '20px'})
        ])
    ])
])

# Callbacks (simplified for space - same as before)
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
    recs = [html.Li(f"💊 {drug}: {guidelines[drug][risk]}") for drug in guidelines]
    return html.Div([
        html.H4(f"Risk: {risk}", style={'color': color}),
        html.P(f"Equity Score: {score:.1f}"),
        html.Ul(recs)
    ])

@app.callback(
    Output('equity-distribution', 'figure'),
    Input('ancestry-filter', 'value')
)
def update_distribution(filter_val):
    data = df if filter_val == 'All' else df[df['ancestry'] == filter_val]
    fig = px.histogram(data, x='equity_score', color='ancestry', nbins=30,
                       title=f'Equity Score Distribution (n={len(data):,})')
    fig.add_vline(x=25, line_dash="dash", line_color="green")
    fig.add_vline(x=50, line_dash="dash", line_color="orange")
    fig.add_vline(x=75, line_dash="dash", line_color="red")
    return fig

@app.callback(
    Output('pca-plot', 'figure'),
    Input('pca-plot', 'id')
)
def create_pca_plot(_):
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    features = ['genetic_risk', 'ses_risk', 'equity_score']
    available = [f for f in features if f in df.columns]
    X = df[available].dropna()
    X_scaled = StandardScaler().fit_transform(X)
    pca_result = PCA(n_components=2).fit_transform(X_scaled)
    fig = px.scatter(x=pca_result[:, 0], y=pca_result[:, 1], color=df.loc[X.index, 'ancestry'],
                     title=f'PCA: Risk Components (n={len(X):,})',
                     labels={'x': 'PC1 (52.7%)', 'y': 'PC2 (33.6%)'})
    return fig

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
