import json
import os
from decimal import Decimal

import psycopg2
import psycopg2.extras
from aiohttp import web


def _json_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _dumps(obj):
    return json.dumps(obj, default=_json_default)


def _get_conn():
    host = os.environ["POSTGRES_HOST"].split(":")[0]
    port = int(os.environ.get("POSTGRES_PORT", os.environ["POSTGRES_HOST"].split(":")[1] if ":" in os.environ["POSTGRES_HOST"] else "5432"))
    return psycopg2.connect(
        host=host,
        port=port,
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname="mev_inspect",
    )


def _query(sql, params=()):
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]


async def get_arbitrages(request):
    limit = min(int(request.rel_url.query.get("limit", "50")), 500)
    rows = _query(
        """
        SELECT block_number, transaction_hash, account_address,
               profit_token_address, start_amount, end_amount, profit_amount,
               protocols, error
        FROM arbitrages
        ORDER BY block_number DESC
        LIMIT %s
        """,
        (limit,),
    )
    return web.Response(text=_dumps(rows), content_type="application/json")


async def get_sandwiches(request):
    limit = min(int(request.rel_url.query.get("limit", "50")), 500)
    rows = _query(
        """
        SELECT block_number, sandwicher_address,
               frontrun_swap_transaction_hash, backrun_swap_transaction_hash,
               profit_token_address, profit_amount
        FROM sandwiches
        ORDER BY block_number DESC
        LIMIT %s
        """,
        (limit,),
    )
    return web.Response(text=_dumps(rows), content_type="application/json")


async def get_liquidations(request):
    limit = min(int(request.rel_url.query.get("limit", "50")), 500)
    rows = _query(
        """
        SELECT block_number, transaction_hash, liquidated_user, liquidator_user,
               protocol, debt_token_address, debt_purchase_amount,
               received_amount, received_token_address, error
        FROM liquidations
        ORDER BY block_number DESC
        LIMIT %s
        """,
        (limit,),
    )
    return web.Response(text=_dumps(rows), content_type="application/json")


async def get_health(request):
    return web.Response(text="ok")


async def get_index(request):
    html = """<!DOCTYPE html>
<html>
<head><title>mev-inspect</title></head>
<body>
<h1>mev-inspect</h1>
<ul>
  <li><a href="/arbitrages">/arbitrages</a> — recent arbitrages</li>
  <li><a href="/sandwiches">/sandwiches</a> — recent sandwich attacks</li>
  <li><a href="/liquidations">/liquidations</a> — recent liquidations</li>
</ul>
<p>Append <code>?limit=N</code> to any endpoint (max 500).</p>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


app = web.Application()
app.router.add_get("/", get_index)
app.router.add_get("/health", get_health)
app.router.add_get("/arbitrages", get_arbitrages)
app.router.add_get("/sandwiches", get_sandwiches)
app.router.add_get("/liquidations", get_liquidations)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    web.run_app(app, host="0.0.0.0", port=port)
