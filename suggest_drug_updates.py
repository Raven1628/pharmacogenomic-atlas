# suggest_drug_updates.py
# Suggest drug guideline updates based on recent literature

import pandas as pd
import json
from datetime import datetime

def review_literature_updates():
    print("="*60)
    print("PHARMACOGENOMIC LITERATURE REVIEW")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        updates_df = pd.read_csv('data/processed/literature_updates.csv')
        print(f"\n📚 Found {len(updates_df)} recent articles to review\n")
        
        # Group by drug
        for drug in updates_df['drug'].unique():
            drug_articles = updates_df[updates_df['drug'] == drug]
            print(f"\n{'='*50}")
            print(f"💊 DRUG: {drug}")
            print(f"{'='*50}")
            
            for _, article in drug_articles.iterrows():
                print(f"\n📄 PMID: {article['pmid']}")
                print(f"📅 Year: {article['year']}")
                print(f"📝 Title: {article['title']}")
                print(f"🔗 URL: {article['url']}")
                print(f"⚡ Potential impact: {article['recommendations_str']}")
                print("-" * 40)
        
        print(f"\n{'='*60}")
        print("ACTION REQUIRED")
        print(f"{'='*60}")
        print("\nTo update drug_config.py:")
        print("1. Review the articles above")
        print("2. Open drug_config.py")
        print("3. Update the recommendations for affected drugs")
        print("4. Commit and push changes")
        print("\nRun 'python auto_update_drug_config.py' for guided updates")
        
    except FileNotFoundError:
        print("\n❌ No literature updates found.")
        print("Run 'python auto_update_literature.py' first to check for new articles.")
    except Exception as e:
        print(f"\nError: {e}")

def auto_update_drug_config():
    """Interactive guided update for drug_config.py"""
    print("\n" + "="*60)
    print("GUIDED DRUG CONFIGURATION UPDATE")
    print("="*60)
    
    try:
        updates_df = pd.read_csv('data/processed/literature_updates.csv')
        
        for drug in updates_df['drug'].unique():
            print(f"\n{'='*50}")
            print(f"Updating {drug}")
            print(f"{'='*50}")
            
            # Display current config would go here
            print("\nWould you like to update recommendations for this drug? (y/n): ", end='')
            if input().lower() == 'y':
                print("\nEnter new recommendations (press Enter to skip):")
                low = input("  Low Risk: ").strip()
                moderate = input("  Moderate Risk: ").strip()
                high = input("  High Risk: ").strip()
                very_high = input("  Very High Risk: ").strip()
                
                if low or moderate or high or very_high:
                    print("\n⚠️ Please manually update drug_config.py with:")
                    print(f"\n    '{drug}': {{")
                    if low: print(f"        'low_risk': '{low}',")
                    if moderate: print(f"        'moderate_risk': '{moderate}',")
                    if high: print(f"        'high_risk': '{high}',")
                    if very_high: print(f"        'very_high_risk': '{very_high}',")
                    print(f"    }},")
    
    except FileNotFoundError:
        print("No literature updates found. Run literature monitor first.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--update':
        auto_update_drug_config()
    else:
        review_literature_updates()
