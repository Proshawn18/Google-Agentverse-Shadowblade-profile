"""
mcp_server.py

A fully compliant MCP server built using the FastMCP and stdio pattern.
This server exposes a toolkit of 12 legendary "weapons" to be discovered and used by other agents.
"""
import random
import sys
import traceback
from typing import Any

from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server. This object will register all our tools.
# The name "armory" acts as a namespace for all tools defined in this file.
mcp = FastMCP("armory")

# --- Define the Core Functions (The "Weapons") ---
# Each function is decorated with @mcp.tool(), which automatically turns it
# into an MCP-compliant tool, using its signature and docstring for the schema.

@mcp.tool()
def forge_broadsword() -> dict[str, Any]:
    """A well-balanced blade against 'The Weaver of Spaghetti Code'."""
    return {
        "weapon_name": "Forged Broadsword", "damage_type": "Slashing", "base_damage": random.randint(110, 140),
        "critical_hit_chance": round(random.uniform(0.15, 0.25), 2),
        "special_effect": "Cleave - has a chance to hit multiple tangled lines of code at once."
    }

@mcp.tool()
def enchant_soulshard_dagger() -> dict[str, Any]:
    """Effective against 'Revolutionary Rewrite' weaknesses like 'The Colossus of a Thousand Patches'."""
    return {
        "weapon_name": "Soulshard Dagger", "damage_type": "Arcane/Piercing", "base_damage": random.randint(120, 135),
        "critical_hit_chance": round(random.uniform(0.25, 0.40), 2),
        "special_effect": "Phase Strike - ignores a portion of the target's legacy complexity."
    }



if __name__ == "__main__":
    print("Starting MCP server with STDIO transport...")
    # The run() method uses stdio by default
    mcp.run()