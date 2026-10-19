# TSGLabs Order Fixtures

Synthetic order lookup API for the TSG Labs Chord build exercise.

## What this is

A small FastAPI service that serves twelve fake order records for a
WhatsApp advance-order food vendor. It is deployed on Railway and
registered as a Custom API tool in Chord so a Chord teammate can look
up an order, verify a payment against it, and update its status.

All data is synthetic. There are no real customers, no live payment
keys, and no connection to any production system.

## Endpoints

- `GET /orders/{order_id}` — return one order, or 404
- `GET /orders?phone={normalized}` — return `order_id` and `event_date`
  for every order on that phone number
- `POST /orders/{order_id}/status` — body `{"status": "..."}`, update
  the in-memory status and return the updated order
- `GET /health` — liveness check

`ORD-211` returns a deliberate 500 to simulate an upstream failure.
`ORD-210` carries a paid amount lower than the amount due, so the
amount-mismatch path can be exercised.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload