"""
RevMatrix AI - Hinglish Voice & Conversational AI Router
Endpoints for voice script generation, audio TTS synthesis metadata, and interactive dialogue simulation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.state import db
from app.engine.hinglish_voice import hinglish_agent
from app.engine.ptp_tracker import ptp_tracker
from app.models.domain import CaseStatus

router = APIRouter(prefix="/api/voice", tags=["Hinglish Voice Agent"])

class DialogueTurnRequest(BaseModel):
    case_id: str
    user_utterance: str

@router.get("/{case_id}/script")
def get_voice_script(case_id: str):
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    script_data = hinglish_agent.generate_call_script(case)
    return script_data

@router.post("/turn")
def process_dialogue_turn(req: DialogueTurnRequest):
    case = db.get_case(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    utterance = req.user_utterance.lower()
    
    # 1. Check for Dispute / Cancellation
    if any(k in utterance for k in ["cancel", "fraud", "scam", "wrong charge", "galti se", "band karo"]):
        case.is_disputed = True
        case.status = CaseStatus.HALTED_DISPUTE
        db.save_case(case)
        return {
            "bot_reply": "Samajh gaya ji. Humne aapka dispute note kar liya hai aur account pe recovery attempts freeze kar diye gaye hain. Thank you!",
            "intent": "DISPUTE_HALTED",
            "action_taken": "FROZEN_ALL_OUTREACH",
            "status": case.status
        }
        
    # 2. Check for PTP (Promise to Pay Later)
    if any(k in utterance for k in ["kal", "friday", "monday", "salary", "next week", "tarik", "tareekh", "baad mein", "later"]):
        ptp = ptp_tracker.register_ptp(case, req.user_utterance)
        db.save_case(case)
        return {
            "bot_reply": f"Bahut badhiya! Humne {ptp.promised_date.strftime('%d %b %Y')} tak ka commitment note kar liya hai. Tab tak aapka account active rahega. Thank you!",
            "intent": "REGISTER_PTP",
            "action_taken": "PTP_HOLD_ACTIVE",
            "promised_date": ptp.promised_date.isoformat(),
            "status": case.status
        }

    # 3. Check for Immediate Payment Agreement
    if any(k in utterance for k in ["haan", "bhej do", "yes", "send", "upi", "link", "ok", "pay"]):
        plan = hinglish_agent.execute(case)
        case.active_intervention = plan
        case.status = CaseStatus.RECOVERED
        case.recovered_amount_inr = case.transaction.amount_inr
        db.save_case(case)
        return {
            "bot_reply": f"Dhanyawad! Maine aapke WhatsApp pe 1-click Razorpay UPI link bhej diya hai. Payment complete hote hi invoice mil jayega.",
            "intent": "PAYMENT_AGREED",
            "action_taken": "DISPATCHED_1CLICK_UPI",
            "payment_link": plan.payload.get("payment_link"),
            "status": case.status
        }

    # Default fallback turn
    return {
        "bot_reply": "Ji main samajh nahi payi. Kya aap 1-click Razorpay UPI se pay karna chahenge, ya hum kisi aur date pe reminder schedule karein?",
        "intent": "CLARIFICATION_PROMPT",
        "action_taken": "AWAITING_USER_INPUT",
        "status": case.status
    }
