from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="TSGLabs Order Fixtures")

ORDERS = {
    "ORD-201": {
        "order_id": "ORD-201",
        "phone_norm": "7063749513",
        "customer_name": "Ada",
        "items": "2 trays jollof, 50 small chops",
        "event_date": "2026-10-23",
        "amount_due_kobo": 8500000,
        "amount_paid_kobo": 8500000,
        "payment_reference": "PSK_ref_201",
        "order_status": "paid_preparing",
    },
    "ORD-202": {
        "order_id": "ORD-202",
        "phone_norm": "8031234567",
        "customer_name": "Tunde",
        "items": "1 celebration cake (2-tier)",
        "event_date": "2026-10-25",
        "amount_due_kobo": 4500000,
        "amount_paid_kobo": None,
        "payment_reference": "PSK_ref_202",
        "order_status": "paid_awaiting_ingredients",
    },
    "ORD-203": {
        "order_id": "ORD-203",
        "phone_norm": "9012345678",
        "customer_name": "Chioma",
        "items": "3 trays fried rice",
        "event_date": "2026-10-22",
        "amount_due_kobo": 6000000,
        "amount_paid_kobo": None,
        "payment_reference": "PSK_ref_203",
        "order_status": "payment_abandoned",
    },
    "ORD-204": {
        "order_id": "ORD-204",
        "phone_norm": "7061112222",
        "customer_name": "Bola",
        "items": "1 tray egusi, 1 tray jollof",
        "event_date": "2026-10-24",
        "amount_due_kobo": 7000000,
        "amount_paid_kobo": None,
        "payment_reference": "PSK_ref_204",
        "order_status": "payment_failed",
    },
    "ORD-205": {
        "order_id": "ORD-205",
        "phone_norm": "8123456789",
        "customer_name": "Ngozi",
        "items": "100 small chops",
        "event_date": "2026-10-26",
        "amount_due_kobo": 5000000,
        "amount_paid_kobo": 5000000,
        "payment_reference": "PSK_ref_205",
        "order_status": "paid_awaiting_ingredients",
    },
    "ORD-206": {
        "order_id": "ORD-206",
        "phone_norm": "8059876543",
        "customer_name": "Emeka",
        "items": "1 tray seafood okra",
        "event_date": "2026-10-20",
        "amount_due_kobo": 5500000,
        "amount_paid_kobo": 5500000,
        "payment_reference": "PSK_ref_206",
        "order_status": "ready_for_dispatch",
    },
    "ORD-207": {
        "order_id": "ORD-207",
        "phone_norm": "7035551212",
        "customer_name": "Fatima",
        "items": "2 trays jollof, 1 tray coleslaw",
        "event_date": "2026-10-21",
        "amount_due_kobo": 9000000,
        "amount_paid_kobo": 9000000,
        "payment_reference": "PSK_ref_207",
        "order_status": "dispatched",
    },
    "ORD-208": {
        "order_id": "ORD-208",
        "phone_norm": "8091112233",
        "customer_name": "Kelechi",
        "items": "50 puff-puff, 50 samosa",
        "event_date": "2026-10-18",
        "amount_due_kobo": 3000000,
        "amount_paid_kobo": 3000000,
        "payment_reference": "PSK_ref_208",
        "order_status": "delivered",
    },
    "ORD-209": {
        "order_id": "ORD-209",
        "phone_norm": "7063749513",
        "customer_name": "Ada",
        "items": "1 tray chicken stew",
        "event_date": "2026-10-30",
        "amount_due_kobo": 4000000,
        "amount_paid_kobo": None,
        "payment_reference": "PSK_ref_209",
        "order_status": "pending_payment",
    },
    "ORD-210": {
        "order_id": "ORD-210",
        "phone_norm": "8154447788",
        "customer_name": "Ify",
        "items": "1 tray fried rice, 1 tray chicken",
        "event_date": "2026-10-27",
        "amount_due_kobo": 6500000,
        "amount_paid_kobo": 3000000,
        "payment_reference": "PSK_ref_210",
        "order_status": "payment_failed",
    },
    "ORD-212": {
        "order_id": "ORD-212",
        "phone_norm": "7063749513",
        "customer_name": "Ada",
        "items": "1 tray jollof",
        "event_date": "2026-10-31",
        "amount_due_kobo": 3500000,
        "amount_paid_kobo": 3500000,
        "payment_reference": "PSK_ref_212",
        "order_status": "dispatched",
    },
}

# ORD-211 is deliberately excluded from normal lookup to simulate an
# upstream API failure. Any request for it returns a 500.

class StatusUpdate(BaseModel):
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if order_id == "ORD-211":
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
    return order


@app.get("/orders")
def lookup_by_phone(phone: str = Query(...)):
    matches = [
        {"order_id": o["order_id"], "event_date": o["event_date"]}
        for o in ORDERS.values()
        if o["phone_norm"] == phone
    ]
    if not matches:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found"},
        )
    return matches


@app.post("/orders/{order_id}/status")
def update_status(order_id: str, body: StatusUpdate):
    if order_id == "ORD-211":
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
    order["order_status"] = body.status
    return order