# Methodology

## 1. Maturity score

- Six dimensions: strategy and value, talent, operating model, technology, data, adoption and scaling. They follow the areas McKinsey's *Rewired* describes as necessary for a digital and AI transformation, with adoption separated out because it is where pilots most often stall.
- Four questions per dimension, each answered 1 (ad hoc) to 5 (leading). A dimension's score is the mean of its four answers. The overall score is the mean of the six dimensions.
- **Gate = 2.0.** A dimension below the gate blocks the use cases that depend on it and triggers a foundation initiative, with its own one-time and running cost.
- **Target = 4.0** ("scaled"). The gap column is measured against it.

Equal weights are a simplification. A real diagnostic would weight questions by evidence and calibrate against a peer set.

## 2. Feasibility and waves

Each use case names the two dimensions it leans on most and a complexity from 1 to 5.

- Feasibility = mean score of those two dimensions − 0.25 × (complexity − 3), limited to the range 1 to 5.
- Wave = 1 + the number of those dimensions below the gate. A use case with complexity 4 or 5 is never placed in wave 1.
- A wave *n* use case starts in year *n* − 1.

## 3. Business case

For each use case, in INR crore:

- Full run-rate benefit = baseline × impact % × adoption × margin. Margin is 1 for cost and risk levers, and the "margin on new revenue" assumption (50% by default) for revenue levers, because extra revenue is not extra profit.
- The one-time cost falls in the start year. From the following year the benefit ramps linearly to full over the use case's ramp period, and the running cost applies every year.
- Foundation initiatives earn nothing themselves: one-time cost in year 0, running cost every year after.
- NPV discounts from year 0 at 12% by default. Payback is the point at which cumulative cash turns positive, interpolated within the year and measured from the start of the programme.

Default assumptions: base impact case, 12% discount rate, 5-year horizon, 80% adoption, no cost overrun, no delay.

**Sensitivity.** The tornado table recomputes portfolio NPV with one driver moved to a downside and an upside value while the rest stay at base. It does not capture drivers moving together.

**Sanity check.** The run-rate benefit is compared with operating profit. McKinsey estimates generative AI could add value equal to 9 to 15 percent of banking operating profits ([Capturing the full value of generative AI in banking](https://www.mckinsey.com/industries/financial-services/our-insights/capturing-the-full-value-of-generative-ai-in-banking)). Bank A's base case lands at 7.8%, below that range, which is what 80% adoption and a 50% revenue margin should produce.

## 4. What is assumed, and what is not known

| Input | Status |
|---|---|
| Bank A baselines (income, costs) | Assumed. Round figures sized for a mid-sized private bank; not taken from any institution |
| Bank A questionnaire answers | Assumed, to produce a common pattern: platform ahead of data and adoption |
| Use-case impact ranges, costs, ramp periods | Assumed. Low, base and high are my estimates and are the weakest input in the model |
| Dimension-to-use-case dependencies | My judgment |
| Gate, target, complexity penalty | Model parameters, chosen for clarity |

Known limits:

- Use cases are valued independently. Two that act on the same cost base (for example the two contact-centre cases) will overlap in practice, so the portfolio total is somewhat overstated.
- Cash flows are pre-tax and ignore inflation and terminal value.
- Foundation costs are fixed amounts and do not scale with the size of the gap.
- There is no peer benchmark. See `data/SOURCES.md`.

## 5. How AI was used

- **In the product:** a language model may reword the memo's opening paragraph. It receives only the drafted paragraph, is told to keep every number and claim, and its reply is rejected if it contains a number absent from the draft, if the model declines, or if the call fails. Everything else in the memo is formatted from the model's tables in code, and a test compares the committed memo with a fresh run.
- **In the build:** the code and first drafts of the documents were written with an AI coding assistant. I chose the scope, the scoring rules and the assumptions, and checked the outputs: the finance functions are tested against hand-computed cases, and the app was run and inspected tab by tab.
