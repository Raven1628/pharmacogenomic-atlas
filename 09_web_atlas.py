# 09_web_atlas.py
# Complete Pharmacogenomic Equity Atlas with UMAP and PCA

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

print("="*60)
print("Pharmacogenomic Equity Atlas - With UMAP Analysis")
print("="*60)

# Load data
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
    print(f"  ✓ Loaded {len(df):,} patient records")
except:
    df = pd.read_csv("data/processed/enhanced_gxe_data.csv")
    print(f"  ✓ Loaded {len(df):,} records")

# Load UMAP coordinates if available
try:
    umap_df = pd.read_csv("data/processed/umap_coordinates.csv")
    print(f"  ✓ Loaded UMAP coordinates for {len(umap_df):,} samples")
    umap_available = True
except:
    umap_available = False
    print("  ⚠ UMAP coordinates not found - run umap_complete_analysis.py first")

def get_ancestry_description(ancestry):
    descriptions = {'AFR': 'African', 'EUR': 'European', 'EAS': 'East Asian',
                    'SAS': 'South Asian', 'AMR': 'Admixed American'}
    return descriptions.get(ancestry, ancestry)

# Drug guidelines
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
                 'High Risk': 'Screen HLA-B*5701', 'Very High Risk': 'Contraindicated'},
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
        html.P(f"Analyzing {len(df):,} patient records | {len(guidelines)} drugs | 5 ancestry groups",
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
                html.P("PCA shows linear relationships in the data."),
                dcc.Loading(dcc.Graph(id='pca-plot'))
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🗺️ UMAP Analysis', children=[
            html.Div([
                html.H3("UMAP Manifold Learning", style={'marginTop': '20px'}),
                html.P("UMAP (Uniform Manifold Approximation and Projection) reveals non-linear patterns in genetic and SES data, often showing clearer separation than PCA."),
                
                html.Div([
                    html.Label("Color By:", style={'fontWeight': 'bold'}),
                    dcc.RadioItems(
                        id='umap-color-by',
                        options=[
                            {'label': ' Ancestry', 'value': 'ancestry'},
                            {'label': ' Risk Category', 'value': 'risk'},
                            {'label': ' Equity Score', 'value': 'equity'},
                            {'label': ' Genetic Risk', 'value': 'genetic'}
                        ],
                        value='ancestry',
                        inline=True,
                        style={'marginTop': '10px'}
                    )
                ], style={'marginBottom': '20px'}),
                
                dcc.Loading(
                    id="loading-umap",
                    type="circle",
                    children=[dcc.Graph(id='umap-plot')]
                ),
                
                html.P("UMAP preserves local structure better than PCA, revealing meaningful clusters of patients with similar risk profiles.",
                       style={'fontSize': '12px', 'color': '#666', 'marginTop': '20px', 'textAlign': 'center'})
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
    recs = [html.Li(f"💊 {drug}: {guidelines[drug][risk]}") for drug in guidelines]
    return html.Div([
        html.H4(f"Risk: {risk}", style={'color': color}),
        html.P(f"Equity Score: {score:.1f}"),
        html.Ul(recs)
    ])

@app.callback(
    Output('risk-warning', 'children'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value'),
    Input('ancestry-input', 'value')
)
def show_risk_warning(ses, genetic, ancestry):
    if not ancestry:
        return html.Div()
    warnings = []
    if ses > 0.8 and genetic > 66:
        warnings.append(html.Div("🔴 HIGH RISK ALERT: Both genetic and SES factors elevated", 
                                 style={'backgroundColor': '#fdedec', 'padding': '10px', 'borderRadius': '10px', 'color': '#e74c3c'}))
    elif genetic > 66:
        warnings.append(html.Div("⚠️ High Genetic Risk - Genotype-guided dosing recommended", 
                                 style={'backgroundColor': '#fdf2e9', 'padding': '10px', 'borderRadius': '10px'}))
    elif ses > 0.7:
        warnings.append(html.Div("⚠️ High SES Vulnerability - Enhanced monitoring recommended", 
                                 style={'backgroundColor': '#fdf2e9', 'padding': '10px', 'borderRadius': '10px'}))
    return html.Div(warnings)

@app.callback(
    Output("download-report", "data"),
    Input("generate-report-btn", "n_clicks"),
    Input('ancestry-input', 'value'),
    Input('ses-slider', 'value'),
    Input('genetic-slider', 'value')
)
def generate_report(n_clicks, ancestry, ses, genetic):
    if n_clicks is None or not ancestry:
        return None
    score = genetic * 0.5 + ses * 50
    report = f"""
    <html>
    <head><title>Pharmacogenomic Report</title></head>
    <body style="font-family: Arial; padding: 40px;">
        <h1>Pharmacogenomic Patient Report</h1>
        <p><strong>Ancestry:</strong> {ancestry}</p>
        <p><strong>SES Score:</strong> {ses:.2f}</p>
        <p><strong>Genetic Risk:</strong> {genetic:.0f}</p>
        <p><strong>Equity Score:</strong> {score:.1f}</p>
        <hr>
        <h3>Recommendations:</h3>
        <ul>
    """
    for drug in guidelines:
        if score < 25:
            rec = guidelines[drug]['Low Risk']
        elif score < 50:
            rec = guidelines[drug]['Moderate Risk']
        elif score < 75:
            rec = guidelines[drug]['High Risk']
        else:
            rec = guidelines[drug]['Very High Risk']
        report += f"<li><strong>{drug}:</strong> {rec}</li>"
    report += "</ul></body></html>"
    return dcc.send_bytes(report.encode(), f"report_{ancestry}.html")

@app.callback(
    Output('drug-select', 'options'),
    Input('drug-search', 'value')
)
def filter_drugs(search_term):
    if not search_term:
        return [{'label': f"{drug} ({guidelines[drug]['gene']})", 'value': drug} for drug in guidelines]
    search_lower = search_term.lower()
    filtered = [drug for drug in guidelines if search_lower in drug.lower() or search_lower in guidelines[drug]['gene'].lower()]
    return [{'label': f"{drug} ({guidelines[drug]['gene']})", 'value': drug} for drug in filtered]

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
        rows.append(html.Tr([html.Td(risk, style={'backgroundColor': color, 'color': 'white'}), html.Td(rec)]))
    return html.Table(rows)

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
    Output('risk-heatmap', 'figure'),
    Input('ancestry-filter', 'value')
)
def update_heatmap(filter_val):
    data = df if filter_val == 'All' else df[df['ancestry'] == filter_val]
    data = data.copy()
    data['risk_group'] = pd.qcut(data['equity_score'], 4, labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    heatmap_data = data.groupby(['ancestry', 'risk_group'])['high_risk'].mean().unstack()
    fig = px.imshow(heatmap_data, title="High Risk Proportion by Ancestry and Risk Level",
                    color_continuous_scale="RdYlGn_r", aspect="auto", text_auto='.2f')
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
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    fig = px.scatter(x=pca_result[:, 0], y=pca_result[:, 1], 
                     color=df.loc[X.index, 'ancestry'],
                     title=f'PCA: Risk Components (n={len(X):,})',
                     labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', 
                             'y': f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)'})
    return fig

@app.callback(
    Output('umap-plot', 'figure'),
    Input('umap-color-by', 'value')
)
def create_umap_plot(color_by):
    if not umap_available:
        fig = go.Figure()
        fig.add_annotation(text="UMAP coordinates not found. Run 'python umap_complete_analysis.py' first",
                           showarrow=False)
        return fig
    
    if color_by == 'ancestry':
        fig = px.scatter(umap_df, x='UMAP1', y='UMAP2', color='ancestry',
                         title='UMAP Projection - Colored by Ancestry',
                         color_discrete_map={'AFR': '#e41a1c', 'EUR': '#377eb8', 
                                            'EAS': '#4daf4a', 'SAS': '#984ea3', 'AMR': '#ff7f00'})
    elif color_by == 'risk':
        fig = px.scatter(umap_df, x='UMAP1', y='UMAP2', color='risk_category',
                         title='UMAP Projection - Colored by Risk Category',
                         color_discrete_map={'Low Risk': '#27ae60', 'Moderate Risk': '#f39c12',
                                            'High Risk': '#e67e22', 'Very High Risk': '#e74c3c'})
    elif color_by == 'equity':
        fig = px.scatter(umap_df, x='UMAP1', y='UMAP2', color='equity_score',
                         title='UMAP Projection - Colored by Equity Score',
                         color_continuous_scale='RdYlGn_r')
    else:
        fig = px.scatter(umap_df, x='UMAP1', y='UMAP2', color='genetic_risk',
                         title='UMAP Projection - Colored by Genetic Risk',
                         color_continuous_scale='viridis')
    
    fig.update_traces(marker=dict(size=5, opacity=0.6))
    fig.update_layout(height=600)
    return fig

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
