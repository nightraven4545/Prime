# Method and limits

How the diagnostic turns answers and baselines into a recommendation, what it assumes, and where it stops being reliable.

## How is AI maturity scored?

- Six areas: strategy and value, talent, operating model, technology, data, and adoption and scaling. Adoption has its own area because it is where AI pilots most often stall.
- Four questions per area, each answered from 1 (ad hoc) to 5 (leading). An area's score is the average of its four answers; the overall score is the average of the six areas.
- **Gate = 2.** An area below the gate holds back every use case that depends on it and adds a foundation initiative, with its own one-off and running cost.
- **Target = 4** ("scaled"). The gap shown on the maturity page is measured against it.

All questions carry equal weight. That keeps the tool easy to follow; a real assessment would weight questions by evidence and compare against peer banks.

## How are use cases prioritised?

Each use case names the two areas it depends on most and a complexity from 1 to 5.

- **Feasibility** = average score of those two areas, minus 0.25 for each step of complexity above 3 (plus 0.25 for each step below), kept between 1 and 5.
- **Wave** = 1 plus the number of those areas below the gate. A use case of complexity 4 or 5 never goes in wave 1.
- A wave *n* use case starts in year *n* − 1.

## How is the business case calculated?

For each use case, in the bank's currency:

- **Yearly benefit at full ramp** = baseline × impact % × adoption × margin. Margin is 1 for cost and risk savings, and the "margin on new revenue" assumption (50% by default) for revenue gains, because extra revenue is not all extra profit.
- The one-off cost falls in the start year. The benefit then ramps up in a straight line over the use case's ramp period; the running cost applies every year after the start.
- Foundation initiatives earn nothing on their own: one-off cost in year 0, running cost every year after.
- **Net present value** discounts each year's cash from year 0, at 12% by default. **Payback** is when the running total turns positive, measured from the start of the programme.

Defaults: base impact case, 12% discount rate, 5-year horizon, 80% adoption, no cost overrun.

**What moves the answer.** The sensitivity chart recalculates the portfolio's value with one assumption moved to a low and a high value while the rest stay at their defaults. It does not show what happens when several assumptions move together.

## What is assumed?

| Input | Where it comes from |
|---|---|
| Sample Bank's income and cost baselines | Assumed. Round figures sized for a mid-sized private bank, not taken from any real institution |
| Sample Bank's questionnaire answers | Assumed, to show a common pattern: technology ahead of data and adoption |
| Each use case's impact range, cost and ramp period | Assumed. The low, base and high cases are estimates and the weakest input in the model |
| Which areas each use case depends on | Judgement |
| Gate, target and complexity adjustment | Model settings, chosen to keep the logic easy to follow |

## Known limits

- Use cases are valued one at a time. Two that act on the same cost (for example two contact-centre tools) would overlap in practice, so the portfolio total is somewhat high.
- Cash flows are pre-tax and ignore inflation and value beyond the horizon.
- Foundation costs are fixed amounts and do not grow with the size of the gap.
- There is no comparison with peer banks yet.

## How are AI answers checked?

The "Try the AI answer checks" page runs the same code that checks answers in the filings-analysis work in progress:

- **Citation check.** Every quote an answer cites must appear word for word in the source passage, and the answer's figure must appear in the quote or come from a recorded calculation.
- **Query safety.** The AI can read reported figures from a database only through a single read-only query, on approved tables, with a row limit. Anything else is refused before it runs.
- **Number reading.** Report figures are read with their sign and scale (thousand, lakh, million, crore, billion), which is where silent errors most often start.
- **Calculator.** Arithmetic goes through a calculator that accepts numbers and operators only, never code.
- **Uncertainty.** Accuracy from a test set is reported with a resampled 95% interval, so a small test is not read as a precise result.

## How was AI used to build this?

The code and first drafts of the text were written with an AI coding assistant. The scope, scoring rules and assumptions were chosen and reviewed by the author, and the results are checked by automated tests: the finance formulas against hand-worked cases, and each check against cases it must accept and cases it must refuse.

## Chart colours

Colours were checked with a palette validator for colour-blind separation and contrast in light and dark mode. Colour is never the only signal: areas below the gate are also labelled in text, and every chart has a table view or a written caption.
