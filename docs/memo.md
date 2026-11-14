# Bank A: where AI pays, and what to fix first

*Fictional mid-sized Indian private-sector bank. All figures are in INR crore and are illustrative assumptions, not data about a real bank. See `docs/methodology.md`.*

## Recommendation

Bank A should fund 4 technology-led AI use cases now, spend the first year on 2 foundations (data; adoption and scaling), and hold 3 use cases that do not pay back. Even with those included, the programme has a net present value of ₹626 crore over 5 years at a 12% discount rate, pays back in 2.1 years, and needs ₹183 crore of funding before it turns cash-positive.

Three findings support this.

1. **Technology is ahead of the organization around it.** Bank A scores 2.29 out of 5 overall. Technology is the strongest dimension at 3.25; Data (1.75) and Adoption and scaling (1.75) fall below the 2.0 gate. 14 of 18 use cases depend on a gated dimension, so they cannot start until it is fixed.
2. **The value is real, and about half of it sits in five use cases.** At full ramp the portfolio adds ₹485 crore a year to pre-tax profit, 7.8% of operating profit. The five largest use cases account for 54% of positive NPV.
3. **Not every use case earns its place.** Next-best-offer for retail customers, Relationship-manager copilot for SME banking and Real-time fraud scoring do not recover their cost within 5 years because they start late and ramp slowly. Hold them until the data work is done, then re-run the case; leaving them out raises NPV by ₹34 crore.

## 1. Maturity: strong platform, weak data and adoption

| Dimension | Score (1-5) | Level | Gap to 4 |
|---|---|---|---|
| Strategy and value | 2.50 | Emerging | 1.50 |
| Talent | 2.25 | Emerging | 1.75 |
| Operating model | 2.25 | Emerging | 1.75 |
| Technology | 3.25 | Defined | 0.75 |
| Data | 1.75 | Emerging | 2.25 |
| Adoption and scaling | 1.75 | Emerging | 2.25 |

The pattern is common in banks that invested in cloud and platforms before changing how teams work. Bank A can deploy a model; it struggles to feed it good data and to get frontline staff to use the result. A dimension below 2.0 blocks the use cases that depend on it and triggers a foundation initiative:

- **Data:** Customer and credit data products with named owners and quality checks (₹35 crore one-time, ₹12 crore a year).
- **Adoption and scaling:** Change-management playbook with adoption targets in line managers' scorecards (₹6 crore one-time, ₹5 crore a year).

## 2. Priorities: start where the bank is already capable

Wave 1 holds the use cases with no blocked dimension and moderate complexity: Document extraction for account opening and KYC, Coding assistant for software engineers, Automated testing and legacy code migration and Cloud spend optimisation. Together they are worth ₹343 crore in NPV and each pays back within 1.2 years of the programme start.

| Wave | Use case | Feasibility (1-5) | Run-rate benefit | NPV | Payback |
|---|---|---|---|---|---|
| 1 | Document extraction for account opening and KYC | 2.8 | 53 | 120 | 1.1 years |
| 1 | Coding assistant for software engineers | 3.2 | 43 | 117 | 0.2 years |
| 1 | Automated testing and legacy code migration | 2.8 | 29 | 57 | 1.2 years |
| 1 | Cloud spend optimisation | 3.1 | 17 | 49 | 0.3 years |
| 2 | Service assistant for contact-centre agents | 2.8 | 38 | 63 | 2.0 years |
| 2 | Contract and licence analytics for tech sourcing | 2.4 | 25 | 58 | 1.2 years |
| 2 | Automated reconciliation and exception handling | 2.5 | 35 | 54 | 2.1 years |
| 2 | Marketing content and campaign generation | 3.0 | 24 | 53 | 1.2 years |
| 2 | Self-service chatbot for routine queries | 2.5 | 31 | 39 | 2.3 years |
| 2 | Early-warning model for retail and SME credit | 1.8 | 45 | 36 | 3.1 years |
| 2 | Transaction monitoring alert triage | 1.8 | 31 | 35 | 2.5 years |
| 2 | Knowledge search across policies and procedures | 2.8 | 18 | 32 | 1.6 years |
| 2 | Drafting of regulatory and credit memos | 2.8 | 17 | 30 | 1.6 years |
| 2 | Churn prediction and retention offers | 2.0 | 12 | 0 | 4.1 years |
| 2 | Real-time fraud scoring | 2.2 | 11 | -6 | none |
| 3 | Collections prioritisation and contact strategy | 1.8 | 23 | 20 | 3.1 years |
| 3 | Relationship-manager copilot for SME banking | 1.5 | 14 | -13 | none |
| 3 | Next-best-offer for retail customers | 1.5 | 20 | -15 | none |

Run-rate benefit and NPV are in INR crore. Payback is measured from the start of the programme, so a wave 2 use case carries its one-year wait.

## 3. Business case: ₹626 crore NPV, payback in 2.1 years

| Year | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Net cash flow | -85 | -98 | 166 | 321 | 359 | 370 |

One-time investment across use cases and foundations is ₹301 crore. The run-rate benefit of 7.8% of operating profit sits below the 9 to 15 percent that McKinsey estimates for generative AI in banking ([source](https://www.mckinsey.com/industries/financial-services/our-insights/capturing-the-full-value-of-generative-ai-in-banking)). The gap is deliberate: this case assumes 80% adoption and counts only 50% of new revenue as profit.

**What moves the answer.** Portfolio NPV when one driver changes and the rest stay at base:

| Driver | Downside NPV | Upside NPV |
|---|---|---|
| Impact per use case (low / high case) | 11 | 1,331 |
| Adoption (60% / 100%) | 318 | 934 |
| Schedule (1-year slip / on time) | 352 | 626 |
| Cost (+30% / -10%) | 445 | 687 |
| Discount rate (14% / 10%) | 578 | 679 |
| Margin on new revenue (40% / 60%) | 612 | 640 |

Impact per use case and adoption dominate; cost and discount rate matter far less. In the low-impact case NPV falls to ₹11 crore, close to break-even. Management attention should therefore go to measuring realized benefit and frontline usage, more than to squeezing build cost.

## 4. Roadmap

| Wave | Initiative | Milestone | Success measure |
|---|---|---|---|
| Foundation | Customer and credit data products with named owners and quality checks | Funded and staffed in quarter 1; first release by month 9 | Data score reaches 3 or higher |
| Foundation | Change-management playbook with adoption targets in line managers' scorecards | Funded and staffed in quarter 1; first release by month 9 | Adoption and scaling score reaches 3 or higher |
| 1 | Document extraction for account opening and KYC | Live with the first team by month 6; full rollout by month 12 | Operations cost 6.0% lower at full ramp |
| 1 | Coding assistant for software engineers | Live with the first team by month 6; full rollout by month 12 | Tech dev cost 12.0% lower at full ramp |
| 1 | Automated testing and legacy code migration | Live with the first team by month 6; full rollout by month 12 | Tech dev cost 8.0% lower at full ramp |
| 1 | Cloud spend optimisation | Live with the first team by month 6; full rollout by month 12 | Third party tech spend 4.0% lower at full ramp |
| 2 | Service assistant for contact-centre agents | Build starts once the blocking enabler is in place; live by month 24 | Contact centre cost 15.0% lower at full ramp |
| 2 | Contract and licence analytics for tech sourcing | Build starts once the blocking enabler is in place; live by month 24 | Third party tech spend 6.0% lower at full ramp |
| 2 | Automated reconciliation and exception handling | Build starts once the blocking enabler is in place; live by month 24 | Operations cost 4.0% lower at full ramp |
| 2 | Marketing content and campaign generation | Build starts once the blocking enabler is in place; live by month 24 | Marketing spend 8.0% lower at full ramp |
| 2 | Self-service chatbot for routine queries | Build starts once the blocking enabler is in place; live by month 24 | Contact centre cost 12.0% lower at full ramp |
| 2 | Early-warning model for retail and SME credit | Build starts once the blocking enabler is in place; live by month 24 | Credit cost 4.0% lower at full ramp |
| 2 | Transaction monitoring alert triage | Build starts once the blocking enabler is in place; live by month 24 | Compliance cost 15.0% lower at full ramp |
| 2 | Knowledge search across policies and procedures | Build starts once the blocking enabler is in place; live by month 24 | Operations cost 2.0% lower at full ramp |
| 2 | Drafting of regulatory and credit memos | Build starts once the blocking enabler is in place; live by month 24 | Compliance cost 8.0% lower at full ramp |
| 2 | Churn prediction and retention offers | Build starts once the blocking enabler is in place; live by month 24 | Retail income 0.7% higher at full ramp |
| 2 | Real-time fraud scoring | Hold: negative NPV in this horizon; re-run the case once the foundations are live | Fraud loss 20.0% lower at full ramp |
| 3 | Collections prioritisation and contact strategy | Design in year 2; live in year 3 | Collections cost 12.0% lower at full ramp |
| 3 | Relationship-manager copilot for SME banking | Hold: negative NPV in this horizon; re-run the case once the foundations are live | SME income 1.8% higher at full ramp |
| 3 | Next-best-offer for retail customers | Hold: negative NPV in this horizon; re-run the case once the foundations are live | Retail income 1.2% higher at full ramp |

## 5. Risks and next steps

- **Impact estimates are the weakest input.** Run a four-week measured pilot on the two largest wave 1 use cases before committing wave 2 funding.
- **Adoption is the second-largest swing.** Put usage and realized-benefit targets in line managers' scorecards from the first release.
- **The data foundation is on the critical path** for 11 use cases. Give it a named owner and review it monthly.
- **Next step:** confirm the baselines in section 3 with finance, then take wave 1 and the two foundations to the investment committee.
