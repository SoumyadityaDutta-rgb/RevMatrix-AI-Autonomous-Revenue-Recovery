"""
RevMatrix AI - Mock Case Generator & Seed Dataset
Populates realistic benchmark scenarios covering all 7 track directions, compliance edge cases, and B2B/B2C values.
"""
import uuid
import random
from typing import List
from datetime import datetime, timedelta
from app.models.domain import Customer, TransactionContext, CaseRecord, FailureCategory, CaseStatus

INDIAN_NAMES = [
    ("Rahul Sharma", "+919876543210", "rahul.sharma@example.com", "hinglish"),
    ("Priya Patel", "+919812345678", "priya.p@techcorp.in", "hinglish"),
    ("Amitabh Verma", "+919711223344", "amitabh.v@finverse.io", "english"),
    ("Sneha Kulkarni", "+919920334455", "sneha.k@designstudio.co", "hinglish"),
    ("Vikram Singhania", "+919833445566", "vikram@singhaniagroup.com", "english"),
    ("Ananya Roy", "+919844556677", "ananya.roy@retailhub.in", "hinglish"),
    ("Deepak Gupta", "+919855667788", "deepak@logisticsflow.com", "hindi"),
    ("Rohan Mehta", "+919866778899", "rohan.mehta@cloudscale.ai", "hinglish"),
    ("Kavita Iyer", "+919877889900", "kavita.iyer@fintechhub.org", "english"),
    ("Siddharth Malhotra", "+919888990011", "sid@quickcommerce.in", "hinglish")
]

COMPANIES = [
    "TechNova Solutions Pvt Ltd",
    "Zenith Logistics India",
    "Apex Cloud Infra LLP",
    "Bharat D2C Brands Ltd",
    "FinSecure Paytech",
    "Krypton Analytics Ltd"
]

BANKS = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK", "PAYTM_BANK"]

CART_ITEMS_LIST = [
    ["Wireless Noise-Canceling Headphones", "USB-C Fast Charger"],
    ["Mechanical Ergonomic Keyboard", "Leather Desk Mat"],
    ["Smart Fitness Watch v2", "Extra Silicone Strap"],
    ["Premium Espresso Coffee Maker", "Arabica Beans 500g"],
    ["SaaS Annual Growth Plan - 10 Seats", "Priority Addon"]
]

def generate_mock_cases(count: int = 50) -> List[CaseRecord]:
    cases = []
    
    categories = [
        FailureCategory.PAYMENT_DEGRADATION,
        FailureCategory.CHECKOUT_DROPOFF,
        FailureCategory.FAILED_SUBSCRIPTION,
        FailureCategory.B2B_RECEIVABLES,
        FailureCategory.MANDATE_FAILURE
    ]

    for i in range(count):
        cat = random.choice(categories)
        cust_tuple = random.choice(INDIAN_NAMES)
        cust_id = f"cust_{i+100:03d}"
        
        customer = Customer(
            id=cust_id,
            name=f"{cust_tuple[0]} #{i+1}",
            phone=cust_tuple[1],
            email=f"user{i+1}_{cust_tuple[2]}",
            company_name=random.choice(COMPANIES) if cat == FailureCategory.B2B_RECEIVABLES else None,
            language_preference=cust_tuple[3]
        )

        bank = random.choice(BANKS)
        overdue_days = 0
        error_code = None
        error_desc = None
        cart_items = None
        
        if cat == FailureCategory.PAYMENT_DEGRADATION:
            amount = float(random.randint(500, 8500))
            if bank == "SBI":
                error_code = "BANK_TECHNICAL_ERROR"
                error_desc = "Issuer Switch Down"
            else:
                error_code = random.choice(["BAD_REQUEST_PAYMENT_TIMED_OUT", "GATEWAY_ERROR", "PAYMENT_INSUFFICIENT_FUNDS"])
                error_desc = "Transient authentication network timeout"
                
        elif cat == FailureCategory.CHECKOUT_DROPOFF:
            amount = float(random.randint(1200, 15000))
            cart_items = random.choice(CART_ITEMS_LIST)
            error_code = "CHECKOUT_ABANDONED_BEFORE_PAYMENT"
            error_desc = "User left checkout page during address/payment selection."

        elif cat == FailureCategory.FAILED_SUBSCRIPTION:
            amount = float(random.choice([499, 999, 1499, 2999, 4999, 9999]))
            error_code = random.choice(["CARD_EXPIRED", "PAYMENT_INSUFFICIENT_FUNDS", "OTP_EXPIRED"])
            error_desc = "Recurring subscription auto-charge declined by issuer"

        elif cat == FailureCategory.B2B_RECEIVABLES:
            amount = float(random.randint(25000, 350000))
            overdue_days = random.randint(3, 45)
            error_code = "INVOICE_PAYMENT_OVERDUE"
            error_desc = f"Enterprise invoice unpaid for {overdue_days} days."

        else: # MANDATE_FAILURE
            amount = float(random.choice([799, 1299, 2499, 3999, 6999]))
            error_code = "PAYMENT_INSUFFICIENT_FUNDS" if bank != "PAYTM_BANK" else "BANK_TECHNICAL_ERROR"
            error_desc = "E-mandate / UPI Autopay charge failure"

        tx = TransactionContext(
            transaction_id=f"tx_{uuid.uuid4().hex[:10]}",
            order_id=f"order_{uuid.uuid4().hex[:8]}" if cat == FailureCategory.CHECKOUT_DROPOFF else None,
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}" if cat in [FailureCategory.FAILED_SUBSCRIPTION, FailureCategory.MANDATE_FAILURE] else None,
            invoice_id=f"inv_{uuid.uuid4().hex[:8]}" if cat == FailureCategory.B2B_RECEIVABLES else None,
            amount_inr=amount,
            category=cat,
            error_code=error_code,
            error_description=error_desc,
            issuer_bank=bank,
            payment_method="card" if cat == FailureCategory.FAILED_SUBSCRIPTION else ("mandate" if cat == FailureCategory.MANDATE_FAILURE else "upi"),
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            overdue_days=overdue_days,
            cart_items=cart_items
        )

        # Introduce 2-3 deliberate edge cases (dispute, max attempts) to demonstrate stopping rules
        is_disputed = (i == 4) # Case #5 has active dispute
        attempts_count = 3 if (i == 9) else 0 # Case #10 already reached max attempts

        case = CaseRecord(
            id=f"case_{1001 + i}",
            customer=customer,
            transaction=tx,
            status=CaseStatus.AT_RISK,
            attempts_count=attempts_count,
            is_disputed=is_disputed
        )
        
        cases.append(case)

    return cases
