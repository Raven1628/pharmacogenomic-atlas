
# Drugs@FDA Integration Summary
Generated: 2026-05-04 15:07:32

## Data Source
- Official Drugs@FDA database from FDA website
- Data includes applications, products, submissions, marketing status

## Pharmacogenomic Drugs Extracted
Total PGx-relevant drugs in database: 12

| Drug | Gene | FDA Action |
|------|------|------------|
| Abacavir | HLA-B | Screening required |
| Carbamazepine | HLA-B | Screening recommended |
| Allopurinol | HLA-B | Screening considered |
| Clopidogrel | CYP2C19 | Alternative therapy |
| Warfarin | CYP2C9/VKORC1 | Dose adjustment |
| Codeine | CYP2D6 | Contraindicated |
| Fluorouracil | DPYD | Dose reduction |
| Simvastatin | SLCO1B1 | Alternative therapy |
| Tamoxifen | CYP2D6 | Alternative therapy |
| Celecoxib | CYP2C9 | Dose adjustment |
| Phenytoin | CYP2C9 | Dose adjustment |

## FDA Warning Levels
- **Boxed Warning**: Strongest warning (Abacavir, Carbamazepine, Codeine)
- **Warning**: Significant risk (Clopidogrel, Allopurinol)
- **Dosage Label**: Dosing guidance (Warfarin, Fluorouracil, Simvastatin)

## Integration with Pharmacogenomic Equity Atlas
These FDA data have been integrated into:
1. Clinical calculator recommendations
2. Drug-specific warnings
3. Evidence-based dosing guidance

## Next Steps
- Add more PGx drugs as FDA updates database
- Link to FDA labels for full prescribing information
- Implement FDA adverse event reporting data
