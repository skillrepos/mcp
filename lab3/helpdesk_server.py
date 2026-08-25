# helpdesk_server.py - a small MCP server for a support desk.
#
# The tools below work exactly the same before and after you merge. What
# changes is everything the model has to go on: the tool names, the parameter
# names, the types, and the documentation. That is the whole contract.

from fastmcp import FastMCP

server = FastMCP("HelpDesk", cache_ttl=300, cache_scope="public")

ORDERS = {
    "A-1043": {"status": "shipped", "carrier": "UPS", "eta": "2026-08-27"},
    "A-1044": {"status": "processing", "carrier": None, "eta": "2026-08-30"},
    "B-2210": {"status": "delivered", "carrier": "FedEx", "eta": "2026-08-19"},
}

CUSTOMERS = {
    "A-1043": "Ada Lovelace",
    "A-1044": "Grace Hopper",
    "B-2210": "Alan Turing",
}


@server.tool
def get_data(a: str) -> str:
    return str(ORDERS.get(a, "no record"))


@server.tool
def fetch_info(x: str) -> str:
    return CUSTOMERS.get(x, "no record")


@server.tool
def run(q: str, p: str = "normal") -> str:
    return f"ticket opened on {q} with priority {p}"


if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
