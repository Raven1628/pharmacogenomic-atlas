# add_pca_umap_tabs.py
# Script to add fixed PCA and UMAP tabs to web app

# This will create a new version of 09_web_atlas.py with PCA/UMAP tabs

with open('09_web_atlas.py', 'r') as f:
    content = f.read()

# Find the position to insert new tabs (after the FDA Evidence Levels tab)
insert_pos = content.find("dcc.Tab(label='ℹ️ About'")

if insert_pos != -1:
    new_tabs = '''
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
        
'''
    # Insert new tabs
    content = content[:insert_pos] + new_tabs + content[insert_pos:]
    
    with open('09_web_atlas_with_pca_umap.py', 'w') as f:
        f.write(content)
    print("✓ Created 09_web_atlas_with_pca_umap.py with PCA/UMAP tabs")
else:
    print("Could not find insertion point")
