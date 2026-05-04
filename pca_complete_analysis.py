# Add after Geographic Map tab
dcc.Tab(label='📊 PCA Analysis', value='tab-pca', children=[
    html.Div([
        html.H3("Principal Component Analysis", style={'marginTop': '20px'}),
        html.P("Visualization of genetic ancestry and risk factor relationships."),
        
        html.Div([
            html.Label("Select PCA Plot:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='pca-plot-select',
                options=[
                    {'label': 'Genetic Ancestry', 'value': 'ancestry'},
                    {'label': 'Risk by Ancestry', 'value': 'risk_ancestry'},
                    {'label': 'Risk Category', 'value': 'risk_category'},
                    {'label': 'GxE Interaction', 'value': 'gxe'},
                    {'label': '3D Risk Projection', 'value': '3d'}
                ],
                value='ancestry'
            )
        ], style={'width': '50%', 'marginBottom': '20px'}),
        
        dcc.Loading(
            dcc.Graph(id='pca-plot')
        )
    ], style={'padding': '20px'})
])