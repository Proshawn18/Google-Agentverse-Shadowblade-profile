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
        "weapon_name": "Forged Broadsword", "damage_type": "Slashing", "base_damage": random.randint(15, 25),
        "critical_hit_chance": round(random.uniform(0.15, 0.25), 2),
        "special_effect": "Cleave - has a chance to hit multiple tangled lines of code at once."
    }

@mcp.tool()
def enchant_soulshard_dagger() -> dict[str, Any]:
    """Effective against 'Revolutionary Rewrite' weaknesses like 'The Colossus of a Thousand Patches'."""
    return {
        "weapon_name": "Soulshard Dagger", "damage_type": "Arcane/Piercing", "base_damage": random.randint(12, 18),
        "critical_hit_chance": round(random.uniform(0.25, 0.40), 2),
        "special_effect": "Phase Strike - ignores a portion of the target's legacy complexity."
    }

@mcp.tool()
def hone_refactoring_sickle() -> dict[str, Any]:
    """Effective against 'Elegant Sufficiency' weaknesses like 'The Weaver of Spaghetti Code'."""
    return {
        "weapon_name": "Refactoring Sickle", "damage_type": "Cleansing", "base_damage": random.randint(10, 15),
        "critical_hit_chance": round(random.uniform(0.10, 0.20), 2),
        "special_effect": "Pruning - improves code health and maintainability with each strike."
    }

@mcp.tool()
def fire_quickstart_crossbow() -> dict[str, Any]:
    """Effective against 'Confrontation with Inescapable Reality' weaknesses like 'Procrastination: The Timeless Slumber'."""
    return {
        "weapon_name": "Quickstart Crossbow", "damage_type": "Initiative", "base_damage": random.randint(1, 5),
        "critical_hit_chance": round(random.uniform(0.9, 1.0), 2),
        "special_effect": "Project Scaffolding - creates a `main.py`, `README.md`, and `requirements.txt`."
    }

@mcp.tool()
def strike_the_gilded_gavel() -> dict[str, Any]:
    """Effective against 'Elegant Sufficiency' weaknesses like 'Perfectionism: The Gilded Cage'."""
    return {
        "weapon_name": "The Gilded Gavel", "damage_type": "Finality", "base_damage": 0, "critical_hit_chance": 1.0,
        "special_effect": "Seal of Shipping - marks a feature as complete and ready for deployment."
    }

@mcp.tool()
def wield_daggers_of_pair_programming() -> dict[str, Any]:
    """Effective against 'Unbroken Collaboration' weaknesses like 'Apathy: The Spectre of "It Works on My Machine"'."""
    return {
        "weapon_name": "Daggers of Pair Programming", "damage_type": "Collaborative", "base_damage": random.randint(40, 60),
        "critical_hit_chance": round(random.uniform(0.30, 0.50), 2),
        "special_effect": "Synergy - automatically resolves merge conflicts and shares knowledge."
    }

@mcp.tool()
def craft_granite_maul() -> dict[str, Any]:
    """Effective against 'Revolutionary Rewrite' weaknesses like 'Dogma: The Zealot of Stubborn Conventions'."""
    return {
        "weapon_name": "Granite Maul", "damage_type": "Bludgeoning", "base_damage": random.randint(25, 40),
        "critical_hit_chance": round(random.uniform(0.05, 0.15), 2),
        "special_effect": "Shatter - has a high chance to ignore the target's 'best practice' armor."
    }

@mcp.tool()
def focus_lens_of_clarity() -> dict[str, Any]:
    """Effective against 'Elegant Sufficiency' weaknesses by revealing the truth behind 'Obfuscation'."""
    return {
        "weapon_name": "Lens of Clarity", "damage_type": "Revelation", "base_damage": 0, "critical_hit_chance": 1.0,
        "special_effect": "Reveal Constants - highlights all magic numbers and suggests converting them to named constants."
    }

@mcp.tool()
def scribe_with_codex_of_openapi() -> dict[str, Any]:
    """Effective against 'Confrontation with Inescapable Reality' weaknesses like 'Hype: The Prophet of Alpha Versions'."""
    return {
        "weapon_name": "Codex of OpenAPI", "damage_type": "Documentation", "base_damage": 5,
        "critical_hit_chance": round(random.uniform(0.5, 0.8), 2),
        "special_effect": "Clarity - makes an API discoverable and usable by other agents and teams."
    }


if __name__ == "__main__":
    print("Starting MCP server with STDIO transport...")
    # The run() method uses stdio by default
    mcp.run()