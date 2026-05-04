from flask import Flask, jsonify, render_template_string
import pandas as pd
import os

app = Flask(__name__)
server = app

# Load data with error handling
try:
    df = pd.read_csv("data/processed/pharmacogenomic_equity_scores.csv")
    data_loaded = True
except:
    data_loaded = False
    df = None

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Pharmacogenomic Equity Atlas</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: white; padding: 40px 20px; }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { font-size: 1.2em; opacity: 0.9; }
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 { color: #667eea; margin-bottom: 20px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .drug-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .drug-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 3px solid #667eea;
        }
        .drug-name { font-weight: bold; color: #667eea; }
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .status-online { background: #27ae60; color: white; }
        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .card { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Pharmacogenomic Equity Atlas</h1>
            <p class="subtitle">Integrating Genetics, Environment, and Clinical Guidelines</p>
            <p><span class="status-badge status-online">✅ Server Online</span></p>
        </div>
        
        <div class="card">
            <h2>📊 Platform Status</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{{ patients }}</div>
                    <div>Patient Records</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">10</div>
                    <div>Drugs Supported</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">5</div>
                    <div>Ancestry Groups</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">✅</div>
                    <div>System Active</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>💊 Supported Drugs & PGx Guidelines</h2>
            <div class="drug-list">
                <div class="drug-item"><span class="drug-name">💊 Warfarin</span><br>CYP2C9 - Dose adjustment</div>
                <div class="drug-item"><span class="drug-name">💊 Clopidogrel</span><br>CYP2C19 - Alternative therapy</div>
                <div class="drug-item"><span class="drug-name">💊 Simvastatin</span><br>SLCO1B1 - Alternative statin</div>
                <div class="drug-item"><span class="drug-name">💊 Fluorouracil</span><br>DPYD - Dose reduction</div>
                <div class="drug-item"><span class="drug-name">💊 Codeine</span><br>CYP2D6 - Avoid in PMs</div>
                <div class="drug-item"><span class="drug-name">💊 Tamoxifen</span><br>CYP2D6 - Consider AI</div>
                <div class="drug-item"><span class="drug-name">💊 Phenytoin</span><br>CYP2C9 - Monitor levels</div>
                <div class="drug-item"><span class="drug-name">💊 Atorvastatin</span><br>SLCO1B1 - Use pravastatin</div>
                <div class="drug-item"><span class="drug-name">💊 Capecitabine</span><br>DPYD - Significant reduction</div>
                <div class="drug-item"><span class="drug-name">💊 Carbamazepine</span><br>HLA-B - Screen allele</div>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Key Statistics</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{{ avg_score }}</div>
                    <div>Avg Equity Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ high_risk }}%</div>
                    <div>High Risk Patients</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ top_ancestry }}</div>
                    <div>Highest Risk Ancestry</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔬 How It Works</h2>
            <p><strong>Pharmacogenomic Equity Score (PES)</strong> = (Genetic Risk × 0.5) + (SES Vulnerability × 100 × 0.5)</p>
            <ul style="margin-top: 15px; margin-left: 20px;">
                <li><strong>Genetic Risk:</strong> Based on number of risk alleles in pharmacogenes</li>
                <li><strong>SES Vulnerability:</strong> Area-level social factors (poverty, unemployment, education)</li>
                <li><strong>Higher Score = Higher Risk</strong> of adverse drug reaction</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Pharmacogenomic Equity Score (PES) | Version 2.0</p>
            <p>🔬 Clinical Decision Support Tool | For Research and Educational Use</p>
            <p>🚀 Full interactive dashboard with clinical calculator coming soon!</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    if data_loaded and df is not None:
        patients = len(df)
        avg_score = f"{df['equity_score'].mean():.1f}"
        high_risk = f"{df['high_risk'].mean() * 100:.1f}"
        top_ancestry = df.groupby('ancestry')['high_risk'].mean().idxmax()
    else:
        patients = "Loading..."
        avg_score = "N/A"
        high_risk = "N/A"
        top_ancestry = "N/A"
    
    return render_template_string(HTML,
        patients=patients,
        avg_score=avg_score,
        high_risk=high_risk,
        top_ancestry=top_ancestry
    )

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Pharmacogenomic Equity Atlas"})

@app.route('/api/status')
def api_status():
    return jsonify({
        "service": "Pharmacogenomic Equity Atlas",
        "status": "online",
        "version": "2.0",
        "data_loaded": data_loaded
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
