# auto_update_literature.py
# Automatically monitor PubMed for new pharmacogenetic literature

import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta
import re
import json
import os

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
                    # Handle multiple abstract sections
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
        """Extract potential clinical recommendations from abstract and title"""
        text = (abstract + " " + title).lower()
        recommendations = []
        
        patterns = {
            'dose_adjustment': r'(?:reduce|increase|adjust|modify).?(?:dose|dosing|dosage)',
            'alternative_therapy': r'(?:alternative|switch|replace|avoid|instead of).?(?:therapy|drug|medication|treatment)',
            'monitoring': r'(?:monitor|check|measure|track|follow).?(?:levels|response|toxicity|concentration)',
            'contraindication': r'(?:contraindicated|avoid|do not use|not recommended)',
            'efficacy_change': r'(?:efficacy|effectiveness|response).?(?:reduced|decreased|lower|poor)',
            'toxicity_risk': r'(?:toxicity|adverse|side effect|complication).?(?:increased|higher|risk)'
        }
        
        for rec_type, pattern in patterns.items():
            if re.search(pattern, text):
                recommendations.append(rec_type)
        
        return recommendations if recommendations else ['review_needed']
    
    def generate_markdown_report(self, all_updates):
        """Generate a markdown report for GitHub"""
        if not all_updates:
            return "No new pharmacogenomic literature found in the last 7 days."
        
        report = f"""# 📚 Pharmacogenomic Literature Update
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Articles found:** {len(all_updates)}

## Summary by Drug

"""
        # Group by drug
        drug_summary = {}
        for update in all_updates:
            drug = update['drug']
            if drug not in drug_summary:
                drug_summary[drug] = []
            drug_summary[drug].append(update)
        
        for drug, updates in drug_summary.items():
            report += f"### 💊 {drug}\n"
            report += f"Found {len(updates)} new article(s)\n\n"
            for update in updates:
                report += f"* **{update['title'][:100]}...**\n"
                report += f"  * Year: {update['year']} | PMID: {update['pmid']}\n"
                report += f"  * Potential impact: {', '.join(update['recommendations'])}\n"
                report += f"  * [Read on PubMed]({update['url']})\n\n"
        
        report += "\n## Action Required\n\n"
        report += "Please review these articles and update `drug_config.py` if clinical recommendations have changed.\n"
        report += "Run `python suggest_drug_updates.py` to help with the update process."
        
        return report
    
    def monitor_updates(self, days_back=7):
        """Main monitoring function"""
        print("="*60)
        print(f"LITERATURE MONITOR - Last {days_back} days")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
            
            time.sleep(0.5)  # Be polite to NCBI API
        
        # Save results
        os.makedirs('data/processed', exist_ok=True)
        
        if all_updates:
            df = pd.DataFrame(all_updates)
            # Convert recommendations list to string for CSV
            df['recommendations_str'] = df['recommendations'].apply(lambda x: ', '.join(x))
            df.to_csv('data/processed/literature_updates.csv', index=False)
            
            # Save JSON for GitHub Actions
            with open('data/processed/literature_updates.json', 'w') as f:
                json.dump(all_updates, f, indent=2, default=str)
            
            # Generate markdown report
            report = self.generate_markdown_report(all_updates)
            with open('data/processed/literature_report.md', 'w') as f:
                f.write(report)
            
            print(f"\n{'='*60}")
            print(f"✓ Found {len(all_updates)} new articles")
            print(f"✓ Saved to data/processed/literature_updates.csv")
            print(f"✓ Saved report to data/processed/literature_report.md")
            return all_updates
        else:
            print(f"\n✓ No new articles found in the last {days_back} days")
            # Create empty report
            with open('data/processed/literature_report.md', 'w') as f:
                f.write(f"# Literature Update - {datetime.now().strftime('%Y-%m-%d')}\n\nNo new pharmacogenomic literature found in the last {days_back} days.")
            return None

if __name__ == '__main__':
    monitor = LiteratureMonitor()
    monitor.monitor_updates(days_back=7)
