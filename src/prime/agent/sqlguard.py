"""Gate for the agent's `query_facts` tool: one read-only SELECT over whitelisted tables, row-limited."""

import sqlglot
from sqlglot import exp

ALLOWED_TABLES = frozenset({"facts", "companies", "filings"})
MAX_ROWS = 200


def guard(sql: str, allowed: frozenset[str] = ALLOWED_TABLES, max_rows: int = MAX_ROWS) -> str:
    """Return the query with a LIMIT enforced, or raise ValueError saying why it was refused."""
    try:
        statements = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError as e:
        raise ValueError(f"could not parse SQL: {e}") from e
    if len(statements) != 1 or statements[0] is None:
        raise ValueError("exactly one statement is allowed")
    tree = statements[0]
    if not isinstance(tree, exp.Select | exp.Union):
        raise ValueError("only SELECT queries are allowed")
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command, exp.Copy)
    if any(tree.find(kind) for kind in forbidden):
        raise ValueError("only SELECT queries are allowed")
    cte_names = {cte.alias for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        # A table function such as read_csv('/etc/passwd') parses as a Table wrapping a function.
        if not isinstance(table.this, exp.Identifier):
            raise ValueError("table functions are not allowed")
        if table.db or table.catalog or table.name.lower() not in allowed | cte_names:
            raise ValueError(f"table not allowed: {table.sql()}")
    limit = tree.args.get("limit")
    if limit is None or not limit.expression.is_int or int(limit.expression.name) > max_rows:
        tree = tree.limit(max_rows)
    return tree.sql(dialect="duckdb")
