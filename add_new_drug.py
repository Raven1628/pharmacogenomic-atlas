# add_new_drug.py
# Interactive script to add new drugs to the central database

import sys
import re

def add_new_drug():
    print("="*60)
    print("Add a New Drug to the Pharmacogenomic Equity Atlas")
    print("="*60)
    
    drug_name = input("\nDrug Name (e.g., 'Carbamazepine'): ").strip()
    gene = input(f"Associated gene for {drug_name} (e.g., 'HLA-B'): ").strip()
    
    print("\nEnter recommendations for each risk category:")
    low_risk = input("  Low Risk: ").strip()
    moderate_risk = input("  Moderate Risk: ").strip()
    high_risk = input("  High Risk: ").strip()
    very_high_risk = input("  Very High Risk: ").strip()
    
    print("\nGxE Parameters (for simulation, press Enter for defaults):")
    base_risk = input("  Base risk (default 0.05): ").strip()
    base_risk = float(base_risk) if base_risk else 0.05
    
    genetic_effect = input("  Genetic effect (default 0.15): ").strip()
    genetic_effect = float(genetic_effect) if genetic_effect else 0.15
    
    ses_effect = input("  SES effect (default 0.10): ").strip()
    ses_effect = float(ses_effect) if ses_effect else 0.10
    
    gxe_effect = input("  GxE effect (default 0.20): ").strip()
    gxe_effect = float(gxe_effect) if gxe_effect else 0.20
    
    # Generate the entry
    new_entry = f"""
    '{drug_name}': {{
        'gene': '{gene}',
        'low_risk': '{low_risk}',
        'moderate_risk': '{moderate_risk}',
        'high_risk': '{high_risk}',
        'very_high_risk': '{very_high_risk}',
        'gxe_params': {{
            'base_risk': {base_risk},
            'genetic_effect': {genetic_effect},
            'ses_effect': {ses_effect},
            'gxe_effect': {gxe_effect}
        }}
    }},"""
    
    print("\n" + "="*60)
    print("Copy this into drug_config.py under DRUG_DATABASE:")
    print("="*60)
    print(new_entry)
    print("="*60)
    
    # Option to auto-add
    auto = input("\nAutomatically add to drug_config.py? (y/n): ").strip().lower()
    if auto == 'y':
        with open('drug_config.py', 'r') as f:
            content = f.read()
        
        # Find the last drug entry (look for pattern before the closing brace)
        # Insert before the last '}' in DRUG_DATABASE
        lines = content.split('\n')
        in_drug_db = False
        last_drug_line = -1
        
        for i, line in enumerate(lines):
            if 'DRUG_DATABASE = {' in line:
                in_drug_db = True
            if in_drug_db and line.strip() and line.strip().startswith("'"):
                last_drug_line = i
            if in_drug_db and line.strip() == '}':
                break
        
        if last_drug_line != -1:
            # Insert after the last drug line
            lines.insert(last_drug_line + 1, new_entry)
            with open('drug_config.py', 'w') as f:
                f.write('\n'.join(lines))
            print(f"✓ Added {drug_name} to drug_config.py")
        else:
            print("Could not auto-add. Please add manually.")
    
    print(f"\n✓ {drug_name} has been configured!")
    print("\nDrug classes you can add to DRUG_CLASSES in drug_config.py:")
    print(f"    '{drug_name}']: ['{drug_name}']")

if __name__ == '__main__':
    add_new_drug()
