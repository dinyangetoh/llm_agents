from mcp.server.fastmcp import FastMCP

from support import (
    append_ticket_message as db_append_ticket_message,
    close_ticket as db_close_ticket,
    create_ticket as db_create_ticket,
    escalate_ticket as db_escalate_ticket,
    get_article,
    get_ticket as db_get_ticket,
    get_ticket_thread as db_get_ticket_thread,
    reopen_ticket as db_reopen_ticket,
    search_kb,
    ticket_summary,
    update_ticket as db_update_ticket,
)

mcp = FastMCP("support_server")


@mcp.tool()
async def create_ticket(customer_name: str, issue: str, priority: str) -> str:
    """Create a new support ticket for a customer.

    Args:
        customer_name: Name of the customer
        issue: Short description of the problem
        priority: One of low, medium, high
    """
    t = db_create_ticket(customer_name, issue, priority)
    return ticket_summary(t)


@mcp.tool()
async def get_ticket(ticket_id: str) -> str:
    """Load a ticket by id and return its full details.

    Args:
        ticket_id: The ticket identifier (e.g. TKT-xxxxxxxxxx)
    """
    return ticket_summary(db_get_ticket(ticket_id))


@mcp.tool()
async def get_ticket_thread(ticket_id: str) -> str:
    """Return ticket summary plus chronological customer/agent/system messages.

    Use this when the customer references a ticket id (TKT-...) for follow-up context.
    If the ticket is resolved, the text explains how to reopen or open a new ticket.

    Args:
        ticket_id: The ticket identifier (e.g. TKT-xxxxxxxxxx)
    """
    return db_get_ticket_thread(ticket_id)


@mcp.tool()
async def append_ticket_message(ticket_id: str, role: str, body: str) -> str:
    """Append a message to the ticket thread. Allowed even when the ticket is resolved.

    Roles: customer, agent, system. Log each inbound customer turn with role customer once you know
    the ticket id (including follow-ups). Log the outbound reply with role agent before close_ticket.

    Args:
        ticket_id: The ticket to attach the message to
        role: One of customer, agent, system
        body: Message text
    """
    return db_append_ticket_message(ticket_id, role, body)


@mcp.tool()
async def reopen_ticket(ticket_id: str, reason: str) -> str:
    """Reopen a resolved ticket for continued work on the same issue.

    Prior resolution is copied into internal notes; status becomes open.

    Args:
        ticket_id: The resolved ticket to reopen
        reason: Why the ticket is being reopened
    """
    return db_reopen_ticket(ticket_id, reason)


@mcp.tool()
async def update_ticket(ticket_id: str, notes: str) -> str:
    """Append notes to an open or escalated ticket.

    Args:
        ticket_id: The ticket to update
        notes: Additional notes to append
    """
    return db_update_ticket(ticket_id, notes)


@mcp.tool()
async def escalate_ticket(ticket_id: str, reason: str) -> str:
    """Mark a ticket as escalated and record the reason in notes.

    Args:
        ticket_id: The ticket to escalate
        reason: Why the ticket is being escalated
    """
    return db_escalate_ticket(ticket_id, reason)


@mcp.tool()
async def close_ticket(ticket_id: str, resolution: str) -> str:
    """Resolve a ticket with a final resolution summary.

    Args:
        ticket_id: The ticket to close
        resolution: How the issue was resolved
    """
    return db_close_ticket(ticket_id, resolution)


@mcp.tool()
async def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base by keywords and return matching topics.

    Args:
        query: Free-text query (e.g. password, billing, shipping)
    """
    topics = search_kb(query)
    if not topics:
        return "No matching knowledge base topics."
    return "Matching topics: " + ", ".join(topics)


@mcp.resource("kb://support/{topic}")
async def read_kb_article(topic: str) -> str:
    return get_article(topic)


@mcp.resource("support://tickets/{ticket_id}")
async def read_ticket_resource(ticket_id: str) -> str:
    return ticket_summary(db_get_ticket(ticket_id))


if __name__ == "__main__":
    mcp.run(transport="stdio")
