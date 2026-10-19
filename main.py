from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="TSGLabs Order Fixtures")

# References marked (REAL) are taken from the Paystack test dashboard.
# References marked (PLACEHOLDER) are invented and will return 400 from
# Paystack verify. Use them only to test the verification-error path.
#
# Each order that goes through verification has its own unique reference.
# ORD-214 and ORD-215 are terminal-state rows and never verify, so their
# reference reuse is harmless.

ORDERS = {
    # ── happy path: payment verified, amount matches ──
    "ORD-201": {
        "order_id": "ORD-201",
        "phone_norm": "7063749513",
        "customer_name": "Ada",
        "items": "2 trays jollof, 50 small chops",
        "event_date": "2026-10-23",
        "amount_due_kobo": 5000000,
        "amount_paid_kobo": None,
        "payment_reference": "invpay_1d486f9692e14c13a0c7e17bfff57e07",  # REAL, ₦50,000
        "order_status": "pending_payment",
    },
    "ORD-202": {
        "order_id": "ORD-202",
        "phone_norm": "8031234567",
        "customer_name": "Tunde",
        "items": "1 celebration cake (2-tier)",
        "event_date": "2026-10-25",
        "amount_due_kobo": 750000,
        "amount_paid_kobo": None,
        "payment_reference": "payla-sub-9751ab89c7bd4cad9759f50e0440088b",  # REAL, ₦7,500
        "order_status": "pending_payment",
    },
    "ORD-203": {
        "order_id": "ORD-203",
        "phone_norm": "9012345678",
        "customer_name": "Chioma",
        "items": "3 trays fried rice",
        "event_date": "2026-10-22",
        "amount_due_kobo": 500000,
        "amount_paid_kobo": None,
        "payment_reference": "invpay_c4fd848bb54b4143bfc605e54b5af537",  # REAL, ₦5,000
        "order_status": "pending_payment",
    },
    "ORD-204": {
        "order_id": "ORD-204",
        "phone_norm": "7061112222",
        "customer_name": "Bola",
        "items": "1 tray egusi, 1 tray jollof",
        "event_date": "2026-10-24",
        "amount_due_kobo": 7500000,
        "amount_paid_kobo": None,
        "payment_reference": "payla-sub-51463aa627c645e0bab65251bbbf66fc",  # REAL, ₦75,000
        "order_status": "pending_payment",
    },
    "ORD-205": {
        "order_id": "ORD-205",
        "phone_norm": "8123456789",
        "customer_name": "Ngozi",
        "items": "100 small chops",
        "event_date": "2026-10-26",
        "amount_due_kobo": 4000000,
        "amount_paid_kobo": None,
        "payment_reference": "invpay_0c9c754cf17545d59237f193f40a7c09",  # REAL, ₦40,000
        "order_status": "pending_payment",
    },
    "ORD-206": {
        "order_id": "ORD-206",
        "phone_norm": "8059876543",
        "customer_name": "Emeka",
        "items": "1 tray seafood okra",
        "event_date": "2026-10-20",
        "amount_due_kobo": 1027900,
        "amount_paid_kobo": None,
        "payment_reference": "payla_af20d582462a47749f804bc88c36b9c2",  # REAL, ₦10,279
        "order_status": "pending_payment",
    },
    "ORD-207": {
        "order_id": "ORD-207",
        "phone_norm": "7035551212",
        "customer_name": "Fatima",
        "items": "2 trays jollof, 1 tray coleslaw",
        "event_date": "2026-10-21",
        "amount_due_kobo": 824900,
        "amount_paid_kobo": None,
        "payment_reference": "payla_06c2373b79ba43a29491b34e2d14d97a",  # REAL, ₦8,249
        "order_status": "pending_payment",
    },
    "ORD-208": {
        "order_id": "ORD-208",
        "phone_norm": "8091112233",
        "customer_name": "Kelechi",
        "items": "50 puff-puff, 50 samosa",
        "event_date": "2026-10-18",
        "amount_due_kobo": 621800,
        "amount_paid_kobo": None,
        "payment_reference": "payla_358d030cf0ad4e6d97e12783e79096da",  # REAL, ₦6,218
        "order_status": "pending_payment",
    },

    # ── amount mismatch: Paystack succeeds, amount is short ──
    "ORD-210": {
        "order_id": "ORD-210",
        "phone_norm": "8154447788",
        "customer_name": "Ify",
        "items": "1 tray fried rice, 1 tray chicken",
        "event_date": "2026-10-27",
        "amount_due_kobo": 6500000,   # ₦65,000 due
        "amount_paid_kobo": None,
        "payment_reference": "payla_bf95a567c8d24c1f935df417b48c5620",  # REAL, ₦50,923 — genuinely short
        "order_status": "pending_payment",
    },

    # ── payment failed at Paystack ──
    "ORD-204B": {
        "order_id": "ORD-204B",
        "phone_norm": "7061112222",
        "customer_name": "Bola",
        "items": "1 tray egusi, 1 tray jollof",
        "event_date": "2026-10-24",
        "amount_due_kobo": 50200000,  # ₦502,000
        "amount_paid_kobo": None,
        "payment_reference": "invpay_407558a02f5b420b918915f9b6520a6a",  # REAL, FAILED
        "order_status": "payment_failed",
    },

    # ── verification error: reference does not exist ──
    "ORD-211": {
        "order_id": "ORD-211",
        "phone_norm": "8029998877",
        "customer_name": "Chinedu",
        "items": "1 cake (1-tier)",
        "event_date": "2026-10-29",
        "amount_due_kobo": 3500000,
        "amount_paid_kobo": None,
        "payment_reference": "PSK_ref_does_not_exist_211",  # PLACEHOLDER, will 400
        "order_status": "pending_payment",
    },

    # ── second order on Ada's phone: ambiguity case ──
    "ORD-212": {
        "order_id": "ORD-212",
        "phone_norm": "7063749513",
        "customer_name": "Ada",
        "items": "1 tray jollof",
        "event_date": "2026-10-31",
        "amount_due_kobo": 3500000,
        "amount_paid_kobo": None,
        "payment_reference": "invpay_27da6dbf34424704b5bd027145a396d7",  # REAL, ₦7,207.11
        "order_status": "pending_payment",
    },

    # ── third order on Ada's phone ──
    "ORD-213": {
        "order_id": "ORD-213",
        "phone_norm": "7063749513",
        "customer_name": "Ada",
        "items": "1 tray chicken stew",
        "event_date": "2026-10-30",
        "amount_due_kobo": 824900,
        "amount_paid_kobo": None,
        "payment_reference": "payla_35b5543a90ef4702a6f458d6cf731f2f",  # REAL, ₦8,249
        "order_status": "pending_payment",
    },

    # ── already dispatched, no verification needed ──
    "ORD-214": {
        "order_id": "ORD-214",
        "phone_norm": "8032221111",
        "customer_name": "Yemi",
        "items": "2 trays jollof",
        "event_date": "2026-10-19",
        "amount_due_kobo": 5000000,
        "amount_paid_kobo": 5000000,
        "payment_reference": "invpay_1d486f9692e14c13a0c7e17bfff57e07",  # REAL
        "order_status": "dispatched",
    },

    # ── delivered, terminal state ──
    "ORD-215": {
        "order_id": "ORD-215",
        "phone_norm": "8051112222",
        "customer_name": "Sade",
        "items": "1 tray fried rice",
        "event_date": "2026-10-15",
        "amount_due_kobo": 500000,
        "amount_paid_kobo": 500000,
        "payment_reference": "invpay_c4fd848bb54b4143bfc605e54b5af537",  # REAL
        "order_status": "delivered",
    },
}

# ORD-211 is the deliberate 500 case, simulating an upstream failure.
FAILING_ORDER_IDS = {"ORD-211"}

# Only these status transitions are allowed. Anything else is rejected
# by the backend, so the agent cannot corrupt an order state by calling
# the status endpoint with the wrong value.
ALLOWED_TRANSITIONS = {
    "pending_payment": {"paid_awaiting_ingredients"},
}


class StatusUpdate(BaseModel):
    status: str
    amount_paid_kobo: int | None = None


def normalise_phone(raw: str) -> str:
    """Strip spaces, dashes, brackets and a leading +234/234/0."""
    cleaned = (
        raw.replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
    )
    if cleaned.startswith("+234"):
        cleaned = cleaned[4:]
    elif cleaned.startswith("234"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("0"):
        cleaned = cleaned[1:]
    return cleaned


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def get_order(order_id: str, phone: str | None = Query(default=None)):
    if order_id in FAILING_ORDER_IDS:
        raise HTTPException(
            status_code=500,
            detail={"error": "upstream_unavailable"},
        )
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found"},
        )
    # When a phone number is supplied, the order is only returned if it
    # matches. This moves the identity check out of the prompt and into
    # the service, so a premature lookup cannot retrieve another
    # customer's order.
    if phone is not None and normalise_phone(phone) != order["phone_norm"]:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found"},
        )
    return order


@app.get("/orders")
def lookup_by_phone(phone: str = Query(...)):
    norm = normalise_phone(phone)
    matches = [
        {"order_id": o["order_id"], "event_date": o["event_date"]}
        for o in ORDERS.values()
        if o["phone_norm"] == norm
    ]
    if not matches:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found"},
        )
    return matches


@app.post("/orders/{order_id}/status")
def update_status(order_id: str, body: StatusUpdate):
    if order_id in FAILING_ORDER_IDS:
        raise HTTPException(
            status_code=500,
            detail={"error": "upstream_unavailable"},
        )
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found"},
        )

    current = order["order_status"]
    requested = body.status

    # Idempotent: asking for the state the order is already in is a
    # success and changes nothing. It still records the paid amount if
    # it was previously missing, so a retry can repair an earlier run.
    if current == requested:
        if body.amount_paid_kobo is not None and order["amount_paid_kobo"] is None:
            order["amount_paid_kobo"] = body.amount_paid_kobo
        return order

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if requested not in allowed:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "invalid_transition",
                "from": current,
                "to": requested,
                "allowed": sorted(allowed),
            },
        )

    # A paid transition must carry the verified amount. Refusing a
    # missing amount keeps the record honest: an order cannot read as
    # paid without recording how much was received.
    if requested == "paid_awaiting_ingredients" and body.amount_paid_kobo is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "amount_paid_required"},
        )

    order["order_status"] = requested
    if body.amount_paid_kobo is not None:
        order["amount_paid_kobo"] = body.amount_paid_kobo
    return order