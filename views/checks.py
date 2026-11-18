import streamlit as st

from prime.agent.calc import calculate
from prime.agent.sqlguard import guard
from prime.agent.verify import number_check, quote_check
from prime.evals.metrics import bootstrap_ci
from prime.ingest.normalize import caption_scale, parse_number
from prime.schema import Answer, Citation, Passage

st.title("Try the AI answer checks")
st.markdown(
    "When an AI system answers questions from financial reports, the answer should not be trusted on its "
    "word. These are the checks that run on every answer before it is shown. Each one is plain code with "
    "tests, and you can try it here."
)

cite, sql, numbers, calc, stats = st.tabs(
    [
        "Is the citation real?",
        "Is the query safe?",
        "Reading report numbers",
        "Safe calculator",
        "How sure are we?",
    ]
)

with cite:
    st.markdown(
        "An answer must quote its source **word for word**, and its figure must appear in that quote."
    )
    passage = st.text_area(
        "Source passage",
        "Technology and communications expense was $4,512 million in 2025, up from $4,190 million in 2024.",
    )
    c1, c2 = st.columns([3, 1])
    quote = c1.text_input("Quote the answer cites", "expense was $4,512 million")
    value = c2.number_input("Figure the answer gives", value=4512.0, step=1.0)
    p = Passage(id="p", company="Example", fiscal_year=2025, form="10-K", section_path=[], text=passage)
    answer = Answer(answerable=True, text="", value=value, citations=[Citation(passage_id="p", quote=quote)])
    ok_quote, ok_number = quote_check(answer, {"p": p}), number_check(answer)
    (st.success if ok_quote else st.error)(
        "The quote appears in the passage." if ok_quote else "The quote does not appear in the passage.",
        icon=":material/check_circle:" if ok_quote else ":material/cancel:",
    )
    (st.success if ok_number else st.error)(
        "The figure appears in the quote." if ok_number else "The figure is not in the quote.",
        icon=":material/check_circle:" if ok_number else ":material/cancel:",
    )
    st.caption("Try changing one digit in the quote or the figure.")

with sql:
    st.markdown(
        "An AI agent may look up reported figures in a database. It can only **read**, only from approved "
        "tables, and only a limited number of rows."
    )
    examples = {
        "A normal lookup": (
            "select company, fiscal_year, value\nfrom facts where canonical_metric = 'tech_expense'"
        ),
        "Delete data": "delete from facts",
        "Read a file on the server": "select * from read_csv('/etc/passwd')",
        "An unapproved table": "select * from salaries",
        "Two statements at once": "select 1; drop table facts",
    }
    choice = st.radio("Start from an example", list(examples), horizontal=True)
    query = st.text_area("Query", examples[choice], key=f"sql_{choice}")
    try:
        safe = guard(query)
    except ValueError as e:
        st.error(f"Refused: {e}", icon=":material/block:")
    else:
        st.success("Allowed. This is what would run (note the row limit):", icon=":material/check_circle:")
        st.code(safe, language="sql")

with numbers:
    st.markdown(
        "Reports state numbers in many ways: brackets for negatives, dashes for nothing, and a scale in the "
        "table heading. Getting the scale wrong is the commonest silent error."
    )
    c1, c2 = st.columns(2)
    shown = c1.text_input("Number as printed", "(1,234.5)")
    heading = c2.text_input("Table heading", "₹ in crore")
    parsed, scale = parse_number(shown), caption_scale(heading)
    if parsed is None:
        st.info("Read as: no value (blank, dash or not a number).", icon=":material/info:")
    else:
        full = parsed.scaleb(scale or 0)
        st.metric(
            "Read as",
            f"{full:,.0f}" if scale else f"{parsed:,}",
            f"{parsed:,} × 10^{scale}" if scale else "no scale found in the heading",
            delta_color="off",
            delta_arrow="off",
        )
    st.caption("Recognised scales: thousand, lakh, million, crore, billion, trillion.")

with calc:
    st.markdown(
        "The agent never does arithmetic in its head. It calls a calculator that accepts only numbers "
        "and + − × ÷ and powers, and refuses anything that looks like code."
    )
    expr = st.text_input("Expression", "(4512 - 4190) / 4190 * 100")
    try:
        st.success(f"= {calculate(expr):,.4g}", icon=":material/calculate:")
    except ValueError as e:
        st.error(f"Refused: {e}", icon=":material/block:")
    st.caption("Try `__import__('os')` or `2 ** 1000`.")

with stats:
    st.markdown(
        "A score from a small test is uncertain. The range below is the 95% interval from resampling."
    )
    c1, c2 = st.columns(2)
    n = c1.slider("Questions in the test", 10, 500, 50, 10)
    acc = c2.slider("Share answered correctly", 0.5, 1.0, 0.8, 0.01)
    k = round(n * acc)
    mean, low, high = bootstrap_ci([1.0] * k + [0.0] * (n - k))
    st.metric(
        "Measured accuracy",
        f"{mean:.0%}",
        f"likely between {low:.0%} and {high:.0%}",
        delta_color="off",
        delta_arrow="off",
    )
    st.caption("With 50 questions, a measured 80% could plausibly be anywhere from about 68% to 90%.")
