"""
Agent tools registry — each tool is a callable the ReAct agent can invoke.
Tools will be dynamically registered and validated against the org's enabled_tools config.
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


def get_available_tools(org):
    """Get tools enabled for a specific org."""
    if not hasattr(org, "agent_config"):
        return {}
    enabled = org.agent_config.enabled_tools
    if not enabled:
        return TOOL_REGISTRY  # All tools enabled by default
    return {k: v for k, v in TOOL_REGISTRY.items() if k in enabled}
