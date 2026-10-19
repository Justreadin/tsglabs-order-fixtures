from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="TSGLabs Order Fixtures")

# Your twelve rows go here as a dict keyed by order_id
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
    # ... the other rows
}

class StatusUpdate(BaseModel):
    status: str

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail={"error": "not_found"})
    return order

@app.get("/orders")
def lookup_by_phone(phone: str = Query(...)):
    matches = [
        {"order_id": o["order_id"], "event_date": o["event_date"]}
        for o in ORDERS.values()
        if o["phone_norm"] == phone
    ]
    if not matches:
        raise HTTPException(status_code=404, detail={"error": "not_found"})
    return matches

@app.post("/orders/{order_id}/status")
def update_status(order_id: str, body: StatusUpdate):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail={"error": "not_found"})
    order["order_status"] = body.status
    return order

@app.get("/health")
def health():
    return {"status": "ok"}