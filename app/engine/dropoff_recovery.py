"""
RevMatrix AI - Pillar 2: Checkout Drop-Off Recovery Agent
Rescues abandoned carts and checkouts using dynamic 1-click Razorpay UPI links and tailored incentives.
"""
from typing import Dict, Any
from app.models.domain import CaseRecord, InterventionPlan, RecoveryChannel
from app.razorpay_client import rzp_client
from app.engine.audit_logger import audit_engine

class DropoffRecoveryAgent:
    
    @staticmethod
    def execute(case: CaseRecord) -> InterventionPlan:
        cart_desc = ", ".join(case.transaction.cart_items) if case.transaction.cart_items else "Cart Items"
        amount = case.transaction.amount_inr
        
        # Apply 5% rescue discount incentive for high-intent items if amount > 1000
        discount_applied = 0.0
        final_amount = amount
        if amount >= 1000:
            discount_applied = round(amount * 0.05, 2)
            final_amount = amount - discount_applied
            
        description = f"Checkout Rescue for {case.customer.name} - Items: {cart_desc}"
        
        # Call Razorpay Payment Links API
        rzp_link = rzp_client.create_payment_link(
            amount_inr=final_amount,
            description=description,
            customer_name=case.customer.name,
            customer_phone=case.customer.phone,
            customer_email=case.customer.email,
            expire_by_minutes=120, # 2-hour urgent window
            notes={
                "recovery_source": "revmatrix_dropoff_agent",
                "original_amount": str(amount),
                "discount_inr": str(discount_applied),
                "case_id": case.id
            }
        )
        
        # WhatsApp personalized message payload
        wa_message = (
            f"Hey {case.customer.name}! 👋 We noticed you left {cart_desc} in your checkout. "
            + (f"To help you complete your order, we applied an exclusive 5% instant discount (Save ₹{discount_applied:.0f})! 🎁 " if discount_applied > 0 else "")
            + f"Pay securely in 1-click via UPI / Card: {rzp_link['short_url']}"
        )
        
        plan = InterventionPlan(
            case_id=case.id,
            strategy_name="Checkout Drop-Off 1-Click UPI Rescue",
            channel=RecoveryChannel.WHATSAPP_INTERACTIVE,
            action_description=f"Generated Razorpay 1-Click Payment Link ({rzp_link['id']}) with UPI intent & WhatsApp delivery.",
            razorpay_action_type="create_payment_link",
            payload={
                "payment_link_id": rzp_link["id"],
                "short_url": rzp_link["short_url"],
                "upi_intent_uri": rzp_link["upi_intent_uri"],
                "original_amount": amount,
                "discounted_amount": final_amount,
                "whatsapp_message": wa_message,
                "expires_in_mins": 120
            },
            is_compliant=True
        )
        
        audit_engine.record(
            case_id=case.id,
            event_type="TOOL_EXECUTION",
            actor="DropoffRecoveryAgent",
            details={
                "action": "razorpay.payment_link.create",
                "payment_link_id": rzp_link["id"],
                "amount": final_amount,
                "channel": "WhatsApp"
            }
        )
        
        return plan

dropoff_agent = DropoffRecoveryAgent()
