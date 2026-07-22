from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from src.schemas.ai import TimelineEvent
from src.agents.scam_agent import scam_agent
from src.agents.currency_agent import currency_agent
from src.agents.fraud_network_agent import network_agent
from src.agents.geo_agent import geo_agent
from src.agents.fusion_agent import fusion_agent
from src.agents.copilot_agent import copilot_agent
import time
import structlog

logger = structlog.get_logger()

# Define the State
class AgentState(TypedDict):
    session_id: str
    request_data: dict
    timeline: List[TimelineEvent]
    
    # Outputs
    scam_output: dict | None
    currency_output: dict | None
    network_output: dict | None
    geo_output: dict | None
    fusion_output: dict | None
    copilot_output: dict | None
    
    # Error state
    error: str | None

def _create_timeline_event(step: str, agent: str, status: str, duration_ms: int, confidence: float = None) -> TimelineEvent:
    return TimelineEvent(
        step=step,
        agent=agent,
        status=status,
        duration_ms=duration_ms,
        confidence=confidence
    )

# Nodes
async def node_scam_detection(state: AgentState):
    start = time.time()
    try:
        text = state["request_data"].get("text_content", "")
        if text:
            output = await scam_agent.analyze(text, state["request_data"].get("metadata", {}))
            duration = int((time.time() - start) * 1000)
            state["scam_output"] = output.model_dump()
            state["timeline"].append(_create_timeline_event("Scam Detection", "ScamAgent", "Completed", duration, output.confidence))
    except Exception as e:
        logger.error("Scam detection failed", error=str(e))
        state["timeline"].append(_create_timeline_event("Scam Detection", "ScamAgent", "Failed", int((time.time() - start) * 1000)))
    return state

async def node_currency_analysis(state: AgentState):
    start = time.time()
    try:
        # Simplified: In a real app we'd fetch the image bytes from MinIO via URL
        # For orchestrator workflow, if we pass a flag in metadata, we run it
        if state["request_data"].get("metadata", {}).get("analyze_currency"):
            # Mock image bytes
            output = await currency_agent.analyze(b"mock_image")
            duration = int((time.time() - start) * 1000)
            state["currency_output"] = output.model_dump()
            state["timeline"].append(_create_timeline_event("Currency Analysis", "CurrencyAgent", "Completed", duration, output.confidence))
    except Exception as e:
        logger.error("Currency analysis failed", error=str(e))
        state["timeline"].append(_create_timeline_event("Currency Analysis", "CurrencyAgent", "Failed", int((time.time() - start) * 1000)))
    return state

async def node_network_analysis(state: AgentState):
    start = time.time()
    try:
        metadata = state["request_data"].get("metadata", {})
        phone = metadata.get("phone", "unknown")
        upi = metadata.get("upi", "unknown")
        account = metadata.get("account", "unknown")
        
        output = await network_agent.analyze(phone, upi, account)
        duration = int((time.time() - start) * 1000)
        state["network_output"] = output.model_dump()
        state["timeline"].append(_create_timeline_event("Graph Analysis", "NetworkAgent", "Completed", duration, output.confidence))
    except Exception as e:
        logger.error("Network analysis failed", error=str(e))
        state["timeline"].append(_create_timeline_event("Graph Analysis", "NetworkAgent", "Failed", int((time.time() - start) * 1000)))
    return state

async def node_geo_analysis(state: AgentState):
    start = time.time()
    try:
        metadata = state["request_data"].get("metadata", {})
        district = metadata.get("district", "unknown")
        lat = metadata.get("lat", 0.0)
        lon = metadata.get("lon", 0.0)
        
        output = await geo_agent.analyze(lat, lon, district)
        duration = int((time.time() - start) * 1000)
        state["geo_output"] = output.model_dump()
        state["timeline"].append(_create_timeline_event("Geo Analysis", "GeoAgent", "Completed", duration, output.confidence))
    except Exception as e:
        logger.error("Geo analysis failed", error=str(e))
        state["timeline"].append(_create_timeline_event("Geo Analysis", "GeoAgent", "Failed", int((time.time() - start) * 1000)))
    return state

async def node_threat_fusion(state: AgentState):
    start = time.time()
    try:
        inputs = {
            "scam": state.get("scam_output"),
            "currency": state.get("currency_output"),
            "network": state.get("network_output"),
            "geo": state.get("geo_output")
        }
        # Filter Nones before sending to Fusion
        valid_inputs = {k: v for k, v in inputs.items() if v}
        
        if valid_inputs:
            output = await fusion_agent.analyze(valid_inputs)
            duration = int((time.time() - start) * 1000)
            state["fusion_output"] = output.model_dump()
            state["timeline"].append(_create_timeline_event("Threat Fusion", "FusionAgent", "Completed", duration, output.confidence))
    except Exception as e:
        logger.error("Threat fusion failed", error=str(e))
        state["timeline"].append(_create_timeline_event("Threat Fusion", "FusionAgent", "Failed", int((time.time() - start) * 1000)))
    return state

async def node_officer_copilot(state: AgentState):
    start = time.time()
    try:
        if state.get("fusion_output"):
            output = await copilot_agent.analyze(state["fusion_output"], state["request_data"])
            duration = int((time.time() - start) * 1000)
            state["copilot_output"] = output.model_dump()
            state["timeline"].append(_create_timeline_event("Officer Recommendation", "CopilotAgent", "Completed", duration, output.confidence))
    except Exception as e:
        logger.error("Officer copilot failed", error=str(e))
        state["timeline"].append(_create_timeline_event("Officer Recommendation", "CopilotAgent", "Failed", int((time.time() - start) * 1000)))
    return state

# Build Graph
graph = StateGraph(AgentState)

# Add Nodes
graph.add_node("scam", node_scam_detection)
graph.add_node("currency", node_currency_analysis)
graph.add_node("network", node_network_analysis)
graph.add_node("geo", node_geo_analysis)
graph.add_node("fusion", node_threat_fusion)
graph.add_node("copilot", node_officer_copilot)

# Add Edges
# Start by running parallel agents
graph.set_entry_point("scam") # Simplification for LangGraph, we link start to all parallel nodes
graph.add_edge("scam", "fusion")
graph.add_edge("currency", "fusion")
graph.add_edge("network", "fusion")
graph.add_edge("geo", "fusion")

# Note: In LangGraph, to run nodes in parallel from a single start, we can dispatch them.
# A simpler approach that works out of the box is to chain them or use a conditional router.
# Let's rebuild the graph structure properly for parallel execution using fan-out / fan-in.

class ParallelGraphBuilder:
    def __init__(self):
        self.builder = StateGraph(AgentState)
        self.builder.add_node("scam", node_scam_detection)
        self.builder.add_node("currency", node_currency_analysis)
        self.builder.add_node("network", node_network_analysis)
        self.builder.add_node("geo", node_geo_analysis)
        self.builder.add_node("fusion", node_threat_fusion)
        self.builder.add_node("copilot", node_officer_copilot)
        
        # In LangGraph, adding edges from START to multiple nodes runs them in parallel
        self.builder.add_edge("__start__", "scam")
        self.builder.add_edge("__start__", "currency")
        self.builder.add_edge("__start__", "network")
        self.builder.add_edge("__start__", "geo")
        
        # They fan-in to fusion
        self.builder.add_edge("scam", "fusion")
        self.builder.add_edge("currency", "fusion")
        self.builder.add_edge("network", "fusion")
        self.builder.add_edge("geo", "fusion")
        
        self.builder.add_edge("fusion", "copilot")
        self.builder.add_edge("copilot", END)
        
    def compile(self):
        return self.builder.compile()

ai_workflow = ParallelGraphBuilder().compile()
