# Data sources

## What is in this folder

| File | Contents | Origin |
|---|---|---|
| `questionnaire.yaml` | 24 maturity questions in six dimensions, and the foundation initiative for each | Written for this project |
| `bank_a.yaml` | Baselines and questionnaire answers for a fictional bank | Illustrative assumptions |
| `use_cases.csv` | 18 banking AI use cases with impact ranges, costs and dependencies | Illustrative assumptions |

No figure in this folder describes a real bank.

## One external figure is quoted

The memo compares the portfolio's run-rate benefit with McKinsey's estimate that generative AI could add value equal to 9 to 15 percent of banking operating profits:
<https://www.mckinsey.com/industries/financial-services/our-insights/capturing-the-full-value-of-generative-ai-in-banking>

## Replacing the assumptions with real data

To model a real bank, edit `bank_a.yaml`. Public sources for the baselines:

- **RBI, Statistical Tables Relating to Banks in India** (bank-wise earnings, expenses, employees, select ratios): <https://www.rbi.org.in> → Statistics → Database on Indian Economy.
- **Bank annual reports and investor presentations** for cost-to-income, technology spend and digital transaction share.

Check definitions before comparing banks. Cost-to-income in particular differs between standalone and consolidated accounts and between data aggregators.
