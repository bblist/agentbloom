"""
Agent tools registry — each tool is a callable the ReAct agent can invoke.
Tools are auto-registered via the @register_tool decorator.
"""

# Tool registry
TOOL_REGISTRY = {}


def register_tool(name, description, parameters_schema):
    """Decorator to register a tool for the agent."""
    def decorator(func):
        TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "parameters": parameters_schema,
            "handler": func,
        }
        return func
    return decorator


def get_available_tools(org=None):
    """Get tools enabled for a specific org (or all tools if no org)."""
    if org is None:
        return TOOL_REGISTRY
    if not hasattr(org, "agent_config"):
        return TOOL_REGISTRY
    enabled = org.agent_config.enabled_tools
    if not enabled:
        return TOOL_REGISTRY  # All tools enabled by default
    return {k: v for k, v in TOOL_REGISTRY.items() if k in enabled}


# Import all tool modules to trigger registration
from . import generate_page  # noqa: E402, F401
from . import update_page  # noqa: E402, F401
from . import generate_copy  # noqa: E402, F401
from . import images  # noqa: E402, F401
from . import templates  # noqa: E402, F401
from . import sites  # noqa: E402, F401
from . import knowledge_base  # noqa: E402, F401
from . import design  # noqa: E402, F401
