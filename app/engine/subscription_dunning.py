"""
RevMatrix AI - Pillar 3: Failed Subscription Dunning & Involuntary Churn Recovery
Prevents churn by diagnosing recurring payment failures, offering smart card updates, and generating instant fallback links.
"""
from app.models.domain import CaseRecord, InterventionPlan, RecoveryChannel, DeclineType
from app.razorpay_client import rzp_client
from app.engine.audit_logger import audit_engine

class SubscriptionDunningAgent:
    
    @staticmethod
    def execute(case: CaseRecord) -> InterventionPlan:
        sub_id = case.transaction.subscription_id or f"sub_{case.id}"
        amount = case.transaction.amount_inr
        diagnostic = case.diagnostic
        
        # If hard decline (expired card), immediately dispatch card update / UPI autopay switch link
        if diagnostic and diagnostic.decline_type == DeclineType.HARD:
            rzp_link = rzp_client.create_payment_link(
                amount_inr=amount,
                description=f"Update Payment Method for Subscription {sub_id}",
                customer_name=case.customer.name,
                customer_phone=case.customer.phone,
                customer_email=case.customer.email,
                notes={"action": "update_subscription_payment_method", "subscription_id": sub_id}
            )
            
            dunning_message = (
                f"Hello {case.customer.name}, your recurring subscription ({sub_id}) could not be renewed because your registered card has expired. "
                f"To keep your account active without service interruption, update your payment details or pay via UPI here: {rzp_link['short_url']}"
            )
            
            plan = InterventionPlan(
                case_id=case.id,
                strategy_name="Subscription Hard-Decline Instrument Swap",
                channel=RecoveryChannel.EMAIL_DUNNING,
                action_description="Created Razorpay Payment Link to update expired card & prevent subscription cancellation.",
                razorpay_action_type="create_payment_link",
                payload={
                    "payment_link_id": rzp_link["id"],
                    "short_url": rzp_link["short_url"],
                    "dunning_message": dunning_message,
                    "subscription_id": sub_id
                }
            )
        else:
            # Soft decline: generate instant 1-click fallback link and schedule retry
            rzp_link = rzp_client.create_payment_link(
                amount_inr=amount,
                description=f"Renew Subscription {sub_id}",
                customer_name=case.customer.name,
                customer_phone=case.customer.phone,
                customer_email=case.customer.email,
                notes={"action": "renew_subscription", "subscription_id": sub_id}
            )
            
            plan = InterventionPlan(
                case_id=case.id,
                strategy_name="Subscription Soft-Decline 1-Click Fallback",
                channel=RecoveryChannel.WHATSAPP_INTERACTIVE,
                action_description="Dispatched 1-click UPI renewal link & scheduled smart retry sequence.",
                razorpay_action_type="create_payment_link",
                payload={
                    "payment_link_id": rzp_link["id"],
                    "short_url": rzp_link["short_url"],
                    "subscription_id": sub_id
                }
            )

        audit_engine.record(
            case_id=case.id,
            event_type="TOOL_EXECUTION",
            actor="SubscriptionDunningAgent",
            details={
                "action": "subscription_dunning_dispatch",
                "subscription_id": sub_id,
                "decline_type": diagnostic.decline_type.value if diagnostic else "unknown",
                "amount": amount
            }
        )
        
        return plan

subscription_agent = SubscriptionDunningAgent()
