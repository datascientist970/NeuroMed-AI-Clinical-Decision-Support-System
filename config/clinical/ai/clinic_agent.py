
from typing import TypedDict, List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import os
import google.generativeai as genai
import json
from clinical.models import ClinicalAuditLog
from langgraph.graph import StateGraph
import logging
logger = logging.getLogger("clinical")


class ClinicalState(TypedDict):
    # Input
    input_data: Dict[str, Any]

    # Agent outputs
    patient_profile: Dict[str, Any]
    data_quality_flags: List[str]

    clinical_insights: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: Dict[str, Any]
    explanation: Dict[str, Any]

    # Safety & final
    approval_required: bool
    final_output: Dict[str, Any]
    audit_log: Dict[str, Any]


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def gemini_llm(system_prompt: str, user_payload: dict) -> dict:
    model = genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        system_instruction=system_prompt
    )

    response = model.generate_content(
        contents=[{"role": "user", "parts": [json.dumps(user_payload)]}],
        generation_config={
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
    )

    return json.loads(response.text)

def intake_agent(state: ClinicalState) -> ClinicalState:
    system_prompt = """
    You are a clinical data normalization agent.
    Validate input, normalize vitals, flag missing or abnormal data.
    Do not diagnose. Return strict JSON.
    """

    output = gemini_llm(system_prompt, state["input_data"])

    state["patient_profile"] = output.get("patient_profile", {})
    state["data_quality_flags"] = output.get("data_quality_flags", [])

    return state


def clinical_knowledge_agent(state: ClinicalState) -> ClinicalState:
    system_prompt = """
    You are a clinical knowledge agent.
    Identify possible clinical concerns without diagnosis.
    Use probabilistic language only.
    """

    output = gemini_llm(system_prompt, state["patient_profile"])
    state["clinical_insights"] = output
    return state


def risk_agent(state: ClinicalState) -> ClinicalState:
    system_prompt = """
    You are a risk stratification agent.
    Classify patient risk as LOW, MODERATE, or HIGH.
    Justify clearly. Be conservative.
    """

    payload = {
        "profile": state["patient_profile"],
        "insights": state["clinical_insights"]
    }

    output = gemini_llm(system_prompt, payload)
    state["risk_assessment"] = output

    state["approval_required"] = output.get("risk_level") == "HIGH"
    return state


def recommendation_agent(state: ClinicalState) -> ClinicalState:
    system_prompt = """
    You are a clinical decision-support agent.
    Suggest diagnostic tests and care pathways only.
    No treatment. Include disclaimer.
    """

    payload = {
        "risk": state["risk_assessment"],
        "insights": state["clinical_insights"]
    }

    output = gemini_llm(system_prompt, payload)
    state["recommendations"] = output
    return state


def explainability_agent(state: ClinicalState) -> ClinicalState:
    system_prompt = """
    You explain clinical AI reasoning clearly and transparently.
    No hallucinations. No diagnosis.
    """

    output = gemini_llm(system_prompt, state)
    state["explanation"] = output
    return state


def safety_agent(state: ClinicalState) -> ClinicalState:
    audit = {
        "request_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "agent_chain": [
            "intake",
            "clinical_knowledge",
            "risk",
            "recommendation",
            "explainability",
            "safety"
        ]
    }

    risk_level = state["risk_assessment"].get("risk_level", "UNKNOWN")

    logger.info(
        f"Clinical request processed | risk={risk_level} | approval={state['approval_required']}"
    )

    # Save audit log to DB
    ClinicalAuditLog.objects.create(
        request_id=audit["request_id"],
        timestamp=datetime.utcnow(),
        risk_level=risk_level,
        approval_required=state["approval_required"],
        agents_executed=audit["agent_chain"],
        status="SUCCESS"
    )

    state["audit_log"] = audit

    state["final_output"] = {
        "risk_summary": state["risk_assessment"],
        "clinical_insights": state["clinical_insights"],
        "recommendations": state["recommendations"],
        "explanation": state["explanation"],
        "approval_required": state["approval_required"],
        "audit_log": audit
    }

    return state


graph = StateGraph(ClinicalState)

graph.add_node("intake", intake_agent)
graph.add_node("knowledge", clinical_knowledge_agent)
graph.add_node("risk", risk_agent)
graph.add_node("recommendation", recommendation_agent)
graph.add_node("explainability", explainability_agent)
graph.add_node("safety", safety_agent)

graph.set_entry_point("intake")

graph.add_edge("intake", "knowledge")
graph.add_edge("knowledge", "risk")
graph.add_edge("risk", "recommendation")
graph.add_edge("recommendation", "explainability")
graph.add_edge("explainability", "safety")

clinical_graph = graph.compile()


graph.compile()

if __name__ == "__main__":
    input_data = {
        "patient_id": "P001",
        "age": 65,
        "gender": "male",
        "symptoms": "shortness of breath and chest discomfort",
        "vitals": {
            "heart_rate": 110,
            "blood_pressure": "150/95",
            "temperature": 37.8,
            "oxygen_saturation": 91
        }
    }

    state: ClinicalState = {"input_data": input_data}
    result = clinical_graph.invoke(state)

    print(result["final_output"])