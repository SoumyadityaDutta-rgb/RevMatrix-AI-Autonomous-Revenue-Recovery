"""
RevMatrix AI - Pillar 6: Hinglish Voice Recovery Agent
Generates natural, courteous conversational audio scripts and dialogues for Indian consumers with real-time response parsing.
"""
from typing import Dict, Any, Optional
from app.models.domain import CaseRecord, InterventionPlan, RecoveryChannel
from app.razorpay_client import rzp_client
from app.engine.audit_logger import audit_engine

class HinglishVoiceRecoveryAgent:
    
    @staticmethod
    def generate_call_script(case: CaseRecord) -> Dict[str, Any]:
        """
        Synthesizes dynamic Hinglish voice dialogue tailored to the specific case context.
        """
        cust_name = case.customer.name
        amount = case.transaction.amount_inr
        category = case.transaction.category.value
        
        # 1-Click Razorpay link for immediate fulfillment during call
        rzp_link = rzp_client.create_payment_link(
            amount_inr=amount,
            description=f"Voice Recovery Link for {cust_name}",
            customer_name=case.customer.name,
            customer_phone=case.customer.phone,
            customer_email=case.customer.email,
            notes={"source": "hinglish_voice_agent", "case_id": case.id}
        )

        if category == "failed_subscription":
            script_text = (
                f"Namaste {cust_name} ji! Main RevMatrix support desk se baat kar rahi hoon. "
                f"Aapka monthly subscription payment of ₹{amount:,.0f} technical reason se complete nahi ho paya tha. "
                f"Aapki service pause na ho, isliye kya main aapke WhatsApp pe ek instant 1-click UPI link bhej doon?"
            )
        elif category == "checkout_dropoff":
            script_text = (
                f"Hello {cust_name} ji! Aapne hamari website pe order checkout start kiya tha par payment incomplete reh gaya tha. "
                f"Agar aap abhi complete karna chahte hain, toh humne aapke liye 1-click Razorpay UPI link generate kiya hai. Kya aapko link SMS ya WhatsApp pe chahiye?"
            )
        elif category == "b2b_receivables":
            script_text = (
                f"Namaste {cust_name} ji, main finance accounts team se call kar raha hoon. "
                f"Aapki company ke invoice payment ₹{amount:,.0f} ka follow-up tha. Kya hum is hafte payment process expect kar sakte hain?"
            )
        else:
            script_text = (
                f"Namaste {cust_name} ji, aapka ₹{amount:,.0f} ka transaction bank issue ki wajah se decline ho gaya tha. "
                f"Aap bina kisi delay ke UPI ya card se dobara pay kar sakte hain. Kya main direct payment link share kar doon?"
            )

        return {
            "script_hinglish": script_text,
            "voice_gender": "female",
            "accent": "en-IN",
            "payment_link": rzp_link["short_url"],
            "upi_intent_uri": rzp_link["upi_intent_uri"],
            "call_status": "ready_to_dial",
            "conversation_tree": [
                {
                    "intent": "agree_to_pay_now",
                    "user_triggers": ["haan bhej do", "yes send link", "ok WhatsApp pe bhej do", "sure"],
                    "bot_response": "Thank you! Maine aapke WhatsApp pe Razorpay UPI link bhej diya hai. Sirf 1-click mein payment ho jayegi.",
                    "action": "DISPATCH_PAYMENT_LINK"
                },
                {
                    "intent": "promise_to_pay_later",
                    "user_triggers": ["abhi balance nahi hai Friday ko karunga", "salary 5th ko aayegi", "kal karta hoon", "next week"],
                    "bot_response": "Bilkul koi baat nahi ji! Humne aapka commitment note kar liya hai aur tab tak aapka account active rahega. Have a great day!",
                    "action": "REGISTER_PTP"
                },
                {
                    "intent": "dispute_or_cancelled",
                    "user_triggers": ["maine cancel kar diya tha", "mujhe nahi chahiye", "wrong charge", "fraud"],
                    "bot_response": "Samajh gaya ji. Main turant hamare system mein dispute/cancellation register kar rahi hoon aur koi follow-up call nahi aayegi.",
                    "action": "HALT_DISPUTE"
                }
            ]
        }

    @classmethod
    def execute(cls, case: CaseRecord) -> InterventionPlan:
        voice_data = cls.generate_call_script(case)
        
        plan = InterventionPlan(
            case_id=case.id,
            strategy_name="Hinglish AI Voice Recovery Call",
            channel=RecoveryChannel.HINGLISH_VOICE,
            action_description=f"Generated natural Hinglish IVR voice script with conversational intent tree & 1-click UPI dispatch.",
            razorpay_action_type="voice_outreach_dispatch",
            payload=voice_data,
            is_compliant=True
        )
        
        audit_engine.record(
            case_id=case.id,
            event_type="TOOL_EXECUTION",
            actor="HinglishVoiceRecoveryAgent",
            details={
                "action": "hinglish_voice_script_synthesized",
                "phone": case.customer.phone,
                "amount": case.transaction.amount_inr,
                "link_attached": voice_data["payment_link"]
            }
        )
        
        return plan

hinglish_agent = HinglishVoiceRecoveryAgent()
