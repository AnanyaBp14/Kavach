from fastapi import APIRouter, Request, HTTPException
import uuid
import structlog
from src.schemas.ai import AIAnalysisRequest, AIAnalysisResponse
from src.workflow.graph import ai_workflow
from src.memory.session import memory_layer
from src.producers.kafka_producer import kafka_producer
from src.config.settings import settings

logger = structlog.get_logger()
router = APIRouter()

@router.post("/analyze", response_model=AIAnalysisResponse)
async def trigger_analysis(request: Request, payload: AIAnalysisRequest):
    req_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    corr_id = request.headers.get("x-correlation-id", req_id)
    session_id = str(uuid.uuid4())
    
    # Initialize state
    initial_state = {
        "session_id": session_id,
        "request_data": payload.model_dump(),
        "timeline": [],
        "scam_output": None,
        "currency_output": None,
        "network_output": None,
        "geo_output": None,
        "fusion_output": None,
        "copilot_output": None,
        "error": None
    }
    
    try:
        # Run workflow
        logger.info("Starting AI Workflow", session_id=session_id, complaint_id=payload.complaint_id)
        final_state = await ai_workflow.ainvoke(initial_state)
        
        # Save to memory layer
        await memory_layer.update_context(session_id, final_state)
        
        # Publish events
        await kafka_producer.send_event(
            "ai.analysis.completed", 
            {"session_id": session_id, "complaint_id": payload.complaint_id},
            req_id, corr_id
        )
        
        if final_state.get("fusion_output"):
            await kafka_producer.send_event(
                "threat.fused",
                final_state["fusion_output"],
                req_id, corr_id
            )
            
        if final_state.get("copilot_output"):
            await kafka_producer.send_event(
                "copilot.summary.generated",
                final_state["copilot_output"],
                req_id, corr_id
            )
            
        return AIAnalysisResponse(
            session_id=session_id,
            overall_threat=final_state.get("fusion_output", {}).get("overall_threat"),
            unified_score=final_state.get("fusion_output", {}).get("score"),
            investigation_summary=final_state.get("copilot_output", {}).get("investigation_summary"),
            timeline=final_state.get("timeline", []),
            model_version=settings.REASONING_MODEL,
            workflow_version=settings.WORKFLOW_VERSION,
            prompt_version=settings.PROMPT_VERSION
        )
        
    except Exception as e:
        logger.error("Workflow failed", error=str(e), session_id=session_id)
        raise HTTPException(status_code=500, detail="AI Workflow failed")
