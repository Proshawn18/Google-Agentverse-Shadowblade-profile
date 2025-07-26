from a2a.server.apps import A2AStarletteApplication
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.request_handlers import DefaultRequestHandler
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
import os
import logging
from dotenv import load_dotenv
from shadowblade.agent_executor import ShadowBladeAgentExecutor
import uvicorn
from shadowblade import agent


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

host=os.environ.get("A2A_HOST", "localhost")
port=int(os.environ.get("A2A_PORT",10003))
PUBLIC_URL=os.environ.get("PUBLIC_URL")

class ShadowBladeAgent:
    """An agent representing the Shadowblade character in a game, responding to battlefield commands."""
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self._agent = self._build_agent()
        self.runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="combat_actions",
            name="combat_actions",
            description="""
            This skill enables the Shadowblade to execute intelligent combat maneuvers.
            When commanded to attack a specific monster, the agent will automatically survey its
            arsenal of available weapon tools. It strategically selects the most effective
            weapon by analyzing each tool's description to find a match for the monster's
            stated weakness. Once the optimal weapon is chosen, it executes the attack and
            returns the combat statistics (damage, effects, etc.). 
            """,
            tags=["game", "combat", "shadowblade"],
            examples=[
                "Attack 'The Weaver of Spaghetti Code'.",
                "Take down 'The Colossus of a Thousand Patches' with Revolutionary Rewrite weakness",],
        )
        self.agent_card = AgentCard(
            name="Shadowblade",
            description="""
            A swift and silent operative in the Agentverse game. The Shadowblade responds to
            battlefield commands, executing attacks with a chosen weapon from its arsenal and
            reporting the outcome.
            """,
            url=f"{PUBLIC_URL}",
            version="1.0.0",
            defaultInputModes=ShadowBladeAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=ShadowBladeAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

    def get_processing_message(self) -> str:
        return "Processing the planning request..."

    def _build_agent(self) -> LlmAgent:
        """Builds the LLM agent for the night out planning agent."""
        return agent.root_agent


if __name__ == '__main__':
    try:
        ShadowBladeAgent = ShadowBladeAgent()

        request_handler = DefaultRequestHandler(
            agent_executor=ShadowBladeAgentExecutor(ShadowBladeAgent.runner,ShadowBladeAgent.agent_card),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=ShadowBladeAgent.agent_card,
            http_handler=request_handler,
        )
        logger.info(f"Attempting to start server with Agent Card: {ShadowBladeAgent.agent_card.name}")
        logger.info(f"Server object created: {server}")

        uvicorn.run(server.build(), host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)
