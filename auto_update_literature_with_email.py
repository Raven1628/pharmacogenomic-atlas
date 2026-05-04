# auto_update_literature_with_email.py
# Literature monitor with email alerts

import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta
import re
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration - UPDATE THESE
EMAIL_ADDRESS = "pharmaapp6246@gmail.com"
EMAIL_PASSWORD = "EatShitAsshole6246!"  # Replace with your app password
ALERT_RECIPIENT = "pharmaapp6246@gmail.com"  # Send alerts to same email

class LiteratureMonitor:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.drugs = ['Warfarin', 'Clopidogrel', 'Simvastatin', 'Fluorouracil', 
                      'Codeine', 'Tamoxifen', 'Phenytoin', 'Atorvastatin', 'Capecitabine',
                      'Carbamazepine']
        self.genes = ['CYP2C9', 'CYP2C19', 'SLCO1B1', 'DPYD', 'CYP2D6', 'HLA-B']
        
    def search_pubmed(self, query, days_back=7):
        """Search PubMed for recent articles"""
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
        
        full_query = f'({query}) AND ("{since_date}"[Date - Publication] : "{datetime.now().strftime("%Y/%m/%d")}"[Date - Publication])'
        
        search_url = f"{self.base_url}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': full_query,
            'retmode': 'json',
            'retmax': 50
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            data = response.json()
            return data.get('esearchresult', {}).get('idlist', [])
        except Exception as e:
            print(f"  Search error for {query}: {e}")
            return []
    
    def fetch_article_details(self, pmid_list):
        """Fetch article details for given PMIDs"""
        if not pmid_list:
            return []
        
        fetch_url = f"{self.base_url}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmid_list),
            'retmode': 'xml'
        }
        
        try:
            response = requests.get(fetch_url, params=params, timeout=30)
            root = ET.fromstring(response.content)
            
            articles = []
            for article in root.findall('.//PubmedArticle'):
                title_elem = article.find('.//ArticleTitle')
                title_text = title_elem.text if title_elem is not None else "No title"
                
                abstract = article.find('.//AbstractText')
                abstract_text = ""
                if abstract is not None:
                    abstract_text = abstract.text if abstract.text else ""
                    for section in article.findall('.//AbstractText'):
                        if section.text:
                            abstract_text += section.text + " "
                
                pub_date = article.find('.//PubDate')
                year = "Unknown"
                if pub_date is not None:
                    year_elem = pub_date.find('Year')
                    year = year_elem.text if year_elem is not None else "Unknown"
                
                articles.append({
                    'pmid': article.find('.//PMID').text,
                    'title': title_text,
                    'abstract': abstract_text[:1000] if abstract_text else "",
                    'year': year
                })
            return articles
        except Exception as e:
            print(f"  Fetch error: {e}")
            return []
    
    def extract_recommendations(self, abstract, title):
        """Extract potential clinical recommendations"""
        text = (abstract + " " + title).lower()
        recommendations = []
        
        patterns = {
            'dose_adjustment': r'(?:reduce|increase|adjust|modify).?(?:dose|dosing|dosage)',
            'alternative_therapy': r'(?:alternative|switch|replace|avoid).?(?:therapy|drug|medication)',
            'monitoring': r'(?:monitor|check|measure|track).?(?:levels|response|toxicity)',
            'contraindication': r'(?:contraindicated|avoid|do not use)',
            'efficacy_change': r'(?:efficacy|effectiveness|response).?(?:reduced|decreased)',
            'toxicity_risk': r'(?:toxicity|adverse|side effect).?(?:increased|higher)'
        }
        
        for rec_type, pattern in patterns.items():
            if re.search(pattern, text):
                recommendations.append(rec_type)
        
        return recommendations if recommendations else ['review_needed']
    
    def send_email_alert(self, updates, days_back=7):
        """Send email alert about new literature"""
        if not updates:
            return
        
        subject = f"📚 Pharmacogenomic Literature Alert - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Build email body
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .drug {{ background-color: #e8f4f8; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .article {{ margin: 10px 0; padding: 10px; border-left: 3px solid #3498db; }}
                .footer {{ font-size: 12px; color: #7f8c8d; text-align: center; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔬 Pharmacogenomic Equity Atlas</h2>
                <h3>New Literature Alert - Last {days_back} Days</h3>
            </div>
            
            <p>Dear Research Team,</p>
            <p>Found <strong>{len(updates)} new articles</strong> relevant to your pharmacogenomic drug database:</p>
        """
        
        # Group by drug
        drug_updates = {}
        for update in updates:
            drug = update['drug']
            if drug not in drug_updates:
                drug_updates[drug] = []
            drug_updates[drug].append(update)
        
        for drug, articles in drug_updates.items():
            body += f"""
            <div class="drug">
                <h3>💊 {drug}</h3>
                <p><strong>{len(articles)} new article(s)</strong></p>
            """
            for article in articles:
                body += f"""
                <div class="article">
                    <strong>📄 {article['title'][:150]}...</strong><br>
                    📅 Year: {article['year']} | PMID: {article['pmid']}<br>
                    🔍 Potential impact: {', '.join(article['recommendations'])}<br>
                    🔗 <a href="{article['url']}">Read on PubMed</a>
                </div>
                """
            body += "</div>"
        
        body += f"""
            <div class="footer">
                <p>To update drug recommendations based on these findings:</p>
                <p>1. Review the articles above<br>
                2. Run: python suggest_drug_updates.py<br>
                3. Update drug_config.py manually if needed</p>
                <hr>
                <p>Pharmacogenomic Equity Atlas | Automated Literature Monitor</p>
            </div>
        </body>
        </html>
        """
        
        # Send email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ALERT_RECIPIENT
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"\n📧 Email alert sent to {ALERT_RECIPIENT}")
            return True
        except Exception as e:
            print(f"\n❌ Email error: {e}")
            print("   Make sure you've set up a Gmail App Password")
            return False
    
    def generate_markdown_report(self, all_updates, days_back=7):
        """Generate markdown report"""
        if not all_updates:
            return f"No new pharmacogenomic literature found in the last {days_back} days."
        
        report = f"""# 📚 Pharmacogenomic Literature Update
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Articles found:** {len(all_updates)}

## Summary by Drug

"""
        drug_summary = {}
        for update in all_updates:
            drug = update['drug']
            if drug not in drug_summary:
                drug_summary[drug] = []
            drug_summary[drug].append(update)
        
        for drug, updates in drug_summary.items():
            report += f"### 💊 {drug}\nFound {len(updates)} new article(s)\n\n"
            for update in updates:
                report += f"* **{update['title'][:100]}...**\n"
                report += f"  * Year: {update['year']} | PMID: {update['pmid']}\n"
                report += f"  * Potential impact: {', '.join(update['recommendations'])}\n"
                report += f"  * [Read on PubMed]({update['url']})\n\n"
        
        report += "\n## Action Required\n\n"
        report += "Please review these articles and update `drug_config.py` if clinical recommendations have changed.\n"
        
        return report
    
    def monitor_updates(self, days_back=7):
        """Main monitoring function"""
        print("="*60)
        print(f"📚 PHARMACOGENOMIC LITERATURE MONITOR")
        print(f"   Last {days_back} days")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Email: {EMAIL_ADDRESS}")
        print("="*60)
        
        all_updates = []
        
        for drug in self.drugs:
            print(f"\n🔍 Checking {drug}...")
            pmids = self.search_pubmed(drug, days_back)
            
            if pmids:
                print(f"   Found {len(pmids)} articles")
                articles = self.fetch_article_details(pmids)
                for article in articles:
                    recs = self.extract_recommendations(article['abstract'], article['title'])
                    all_updates.append({
                        'drug': drug,
                        'pmid': article['pmid'],
                        'title': article['title'],
                        'year': article['year'],
                        'recommendations': recs,
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/"
                    })
                    print(f"   ✓ {article['title'][:60]}...")
            else:
                print(f"   No new articles found")
            
            time.sleep(0.5)
        
        # Save results
        import os
        os.makedirs('data/processed', exist_ok=True)
        
        if all_updates:
            df = pd.DataFrame(all_updates)
            df['recommendations_str'] = df['recommendations'].apply(lambda x: ', '.join(x))
            df.to_csv('data/processed/literature_updates.csv', index=False)
            
            with open('data/processed/literature_updates.json', 'w') as f:
                json.dump(all_updates, f, indent=2, default=str)
            
            report = self.generate_markdown_report(all_updates, days_back)
            with open('data/processed/literature_report.md', 'w') as f:
                f.write(report)
            
            print(f"\n{'='*60}")
            print(f"✓ Found {len(all_updates)} new articles")
            print(f"✓ Saved to data/processed/")
            
            # Send email alert
            self.send_email_alert(all_updates, days_back)
            
            return all_updates
        else:
            print(f"\n✓ No new articles found in the last {days_back} days")
            return None

if __name__ == '__main__':
    monitor = LiteratureMonitor()
    monitor.monitor_updates(days_back=7)
