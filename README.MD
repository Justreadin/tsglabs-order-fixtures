# Layla Orders: Order Assurance API

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/status-prototype-orange)](#project-status)

A small FastAPI order-fixture service built for the **TSG Labs Chord build exercise**. It exposes synthetic order records to **Layla Orders**, a Chord-based WhatsApp teammate for the fictional Lagos food vendor **Pepperleaf Kitchen**.

Layla uses the service to retrieve an order, verify its payment with Paystack in test mode, and update the order status only after the required checks succeed.

> **Prototype notice:** This repository is for an evaluation exercise, not production use. The order data is synthetic, storage is in memory, and the service is not connected to a live customer or production payment system. Do not add real customer data or live payment credentials.

## Contents

- [Overview](#overview)
- [System flow](#system-flow)
- [Repository contents](#repository-contents)
- [API reference](#api-reference)
- [Order states and transition rules](#order-states-and-transition-rules)
- [Test fixtures](#test-fixtures)
- [Run locally](#run-locally)
- [Test the API](#test-the-api)
- [Deploy on Railway](#deploy-on-railway)
- [Test through Chord](#test-through-chord)
- [Security and data handling](#security-and-data-handling)
- [Known limitations and production requirements](#known-limitations-and-production-requirements)
- [Related submission documents](#related-submission-documents)
- [External references](#external-references)
- [Use of AI](#use-of-ai)

## Overview

Customers place advance catering and event orders with Pepperleaf Kitchen through WhatsApp. After paying, they may repeatedly ask, “I've paid, where is my order?” The vendor needs to answer using the actual order and payment state, not guesswork.

Layla Orders is designed to:

1. Ask for the order number and the phone number used when placing the order.
2. Retrieve the matching order record.
3. Verify the associated payment reference with Paystack in test mode.
4. Confirm payment only if verification succeeds and the reference, amount, and currency match the order.
5. Update the order record and communicate its recorded status, event date, and delivery window where available.
6. Escalate failed, short, or unverifiable payments and other out-of-scope requests rather than inventing an answer.

This repository contains **the order API only**. The Chord agent, skill instructions, and Chord-side tool configuration are managed separately in the Chord workspace.

## System flow

```mermaid
flowchart TD
    A[Customer messages Layla on WhatsApp simulator] --> B[Layla receives order ID and ordering phone]
    B --> C[Order API returns matching synthetic order]
    C --> D[Layla verifies payment reference with Paystack test mode]
    D --> E{Verification succeeds and order details match?}
    E -- Yes --> F[POST status update with verified amount]
    F --> G[Order status becomes paid_awaiting_ingredients]
    G --> H[Layla reports verified status and recorded delivery window]
    E -- No --> I[Do not mark paid]
    I --> J[Explain that payment cannot be confirmed and escalate]
```

The diagram describes the intended workflow. The API provides order lookup and status-update endpoints; payment verification is performed by the Chord teammate through the configured Paystack integration.

## Repository contents

The repository should contain the API code and the supporting submission documents. Update this list if your committed directory structure differs.

```text
.
├── README.md
├── main.py
├── requirements.txt
├── Procfile
├── PROBLEM_STATEMENT.md
├── DEPLOYMENT_FIELD_NOTES.md
├── GO_LIVE_NOTE.md
├── SKILL.md
└── references/
    ├── business-context.md
    ├── order-statuses.md
    ├── identity-rule.md
    └── escalation-policy.md
```

- `main.py` : FastAPI application and synthetic order fixtures.
- `requirements.txt` : Python dependencies.
- `Procfile` : Railway web-process start command.
- `SKILL.md` and `references/` : Layla's instructions and supporting policy/context files for Chord. These are uploaded/configured in Chord separately from this API service.
- `PROBLEM_STATEMENT.md` : role preference, business context, problem, proposed solution, value hypothesis, and scope.
- `DEPLOYMENT_FIELD_NOTES.md` : issues encountered during setup/testing, observed behaviour, diagnoses, mitigations, and recommended platform improvements.
- `GO_LIVE_NOTE.md` : operator-facing explanation of the workflow, limitations, and requirements before a real launch.

## API reference

The application exposes the following endpoints.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/orders/{order_id}` | Retrieve one order; accepts an optional `phone` query parameter |
| `GET` | `/orders?phone={normalized_phone}` | Find orders associated with a normalized phone number |
| `POST` | `/orders/{order_id}/status` | Request an allowed order-status transition |

When the optional `phone` parameter is supplied to the single-order endpoint and does not match the order's stored phone number, the service returns `404`. The phone-based list endpoint returns the matching orders' identifiers and scheduling details as implemented by the fixture service.

### `GET /health`

Use this endpoint to check whether the application is responding.

Example:

```bash
curl.exe -i "https://<your-service-host>/health"
```

### `GET /orders/{order_id}`

Returns the order fixture for the supplied ID.

Example:

```bash
curl.exe "https://<your-service-host>/orders/ORD-201"
```

Optional phone check:

```bash
curl.exe -i "https://<your-service-host>/orders/ORD-201?phone=7063749513"
```

The phone number must use the normalized format expected by the fixture data. If a supplied number does not match, the endpoint returns `404` rather than disclosing the order.

### `GET /orders?phone={normalized_phone}`

Returns matching orders for a normalized phone number.

Example:

```bash
curl.exe "https://<your-service-host>/orders?phone=7063749513"
```

The response includes order identifiers and scheduling details as implemented by the service. This endpoint is currently a prototype interface; see [Security and data handling](#security-and-data-handling) before considering any real deployment.

### `POST /orders/{order_id}/status`

Requests an order status update. The request body uses JSON:

```json
{
  "status": "paid_awaiting_ingredients",
  "amount_paid_kobo": 5000000
}
```

`amount_paid_kobo` is the verified amount in kobo, not naira. For example, `5000000` kobo is ₦50,000.

#### Status update rules

- Only the transition from `pending_payment` to `paid_awaiting_ingredients` is allowed.
- A transition to `paid_awaiting_ingredients` must include `amount_paid_kobo`; otherwise, the service returns `400` with `amount_paid_required`.
- Repeating the current status is a no-op success, making a repeated status request safe with respect to the status transition.
- Other unsupported transitions return `409` and include the current status, requested status, and allowed transition information.

**Important:** This endpoint enforces the status-transition rules, but the prototype should not be treated as an independently secured payment authority. In a production design, the server must itself validate the payment evidence and the order-to-reference binding before allowing an order to be marked paid. A client-supplied amount alone is not proof of payment.

## Order states and transition rules

The primary successful path is:

```text
pending_payment
       |
       | payment verified; amount/reference/currency match
       v
paid_awaiting_ingredients
```

The service intentionally does not implement the entire fulfilment lifecycle. States such as ingredient sourcing, preparation, dispatch, delivery, refunds, and cancellations require additional business rules and durable records before production use.

## Test fixtures

The fixture dataset includes normal and deliberate failure cases for exercising the agent's decision-making.

| Order | Purpose |
|---|---|
| `ORD-201` | Happy-path order with a delivery window |
| `ORD-207` | Order without a delivery window, to test that the agent does not invent one |
| `ORD-210` | Amount-mismatch scenario: its associated Paystack test transaction is below the order amount due |
| `ORD-211` | Deliberate HTTP `500` response to simulate an order-service failure |

Use synthetic records only. Do not add real customer details or live transaction information to these fixtures.

## Run locally

### Requirements

- Python 3.11 or a compatible Python version supported by the dependencies
- `pip`

### Install dependencies

```bash
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

The API should then be available at `http://127.0.0.1:8000`.

- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- Liveness endpoint: `http://127.0.0.1:8000/health`

The application is configured for local development with `--reload`. Do not use that development command as a production deployment configuration.

## Test the API

Replace `<your-service-host>` with the deployed host or use `http://127.0.0.1:8000` for local testing.

The examples below use `curl.exe`, which avoids the PowerShell alias issue described afterward.

### Health check

```powershell
curl.exe -i "https://<your-service-host>/health"
```

### Retrieve a normal order

```powershell
curl.exe -i "https://<your-service-host>/orders/ORD-201"
```

### Exercise the simulated upstream failure

```powershell
curl.exe -i "https://<your-service-host>/orders/ORD-211"
```

Expected result: HTTP `500`.

### Find orders for a synthetic phone number

```powershell
curl.exe -i "https://<your-service-host>/orders?phone=7063749513"
```

### Request an allowed status update

Use this only against a disposable fixture or test deployment. The amount must correspond to the verified test transaction for that order.

```powershell
curl.exe -i -X POST "https://<your-service-host>/orders/ORD-201/status" `
  -H "Content-Type: application/json" `
  -d "{\"status\":\"paid_awaiting_ingredients\",\"amount_paid_kobo\":5000000}"
```

Do not infer that a payment is valid merely because this endpoint accepts a status update. Payment verification must happen first, and production enforcement should occur server-side.

### PowerShell note

On Windows, use `curl.exe` rather than `curl`. PowerShell may resolve `curl` to `Invoke-WebRequest`, which does not accept the same command-line flags and can produce confusing errors.

## Deploy on Railway

The prototype is deployed on Railway using the `Procfile` start command:

```procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Railway supplies the `PORT` environment variable. The application must bind to `0.0.0.0` and use that port so the service can receive traffic.

After each deployment:

1. Check the deployment logs for a successful application start.
2. Call `/health` on the public domain.
3. Test the relevant endpoints directly with `curl.exe`.
4. Only then test the same workflow through Chord.

If the domain returns `502` while logs suggest the app started, check the service's bound port and Railway's domain/port configuration. Confirm the running deployment rather than assuming that a successful source-code push means the latest code is live.

The current prototype uses in-memory writes. A restart or redeploy can reset changes; this is intentional for repeatable exercise testing and is not suitable for production order management.

## Test through Chord

Layla Orders is configured as a Chord teammate. The order API is one of its external systems; Paystack test mode is used for payment verification. The skill package and tool definitions are managed in Chord separately from this repository.

Two practical testing notes:

1. **Use a fresh conversation for each escalation scenario.** During testing, a Chord conversation that had already entered `human_active` could not be escalated again until it returned to agent handling. The second escalation attempt failed with an invalid state-transition error. See [Deployment Field Notes](DEPLOYMENT_FIELD_NOTES.md) for the observed behaviour and mitigation.
2. **Verify the live deployment before interpreting a result.** A stale deployment can make a working change appear broken. Test the public endpoint directly before testing through Chord.

The expected behaviour is not simply a friendly answer. Check that the underlying tool calls occurred, that payment evidence matches the correct order, and that the order record changed only on the successful path.

## Security and data handling

This is a prototype, and its current safeguards are not sufficient for real customer or payment data.

- Use synthetic customer and order data only.
- Use Paystack test mode and test credentials only.
- Do not commit API keys, access tokens, `.env` files, or other secrets.
- Do not expose this unauthenticated API as a production service.
- Treat order IDs, phone numbers, and payment references as sensitive operational data even when used in a test environment.
- Do not treat a supplied amount as payment evidence; verify the transaction and bind its reference to the correct order.
- Restrict access to the Chord workspace, Railway project, and Paystack dashboard to authorized people.

If credentials have been accidentally committed, revoke or rotate them and remove them from active use. Deleting a secret from the latest commit alone does not invalidate it or remove it from repository history.

## Known limitations and production requirements

The following limitations must be addressed before a real launch:

- **In-memory storage:** order changes do not survive restarts or redeploys. Replace with a persistent database.
- **No authentication or authorization:** endpoints are not protected for production use. Add service authentication, authorization, and appropriate network/access controls.
- **No audit trail:** there is no durable record of who or what changed an order and why. Add auditable events and timestamps.
- **Payment reference seeded in fixtures:** production must create or receive a unique payment reference when a payment link is issued and persistently bind it to the corresponding order.
- **Payment verification boundary:** production server-side logic must verify the Paystack transaction and enforce order ID, reference, status, currency, and expected amount before changing the order to paid.
- **Limited lifecycle:** the API only implements the prototype's payment-related transition, not a complete order fulfilment workflow.
- **No rate limiting or abuse controls:** add suitable request limits, validation, monitoring, and alerting before exposing endpoints.
- **Escalation delivery not confirmed:** the handoff behaviour was tested, but notification delivery to the responsible person must be verified in the target setup.
- **Repeat escalation limitation:** a thread already in `human_active` may not accept a second escalation until it is handed back.

See [Go-Live Note](GO_LIVE_NOTE.md) for the operator-facing launch checklist and [Deployment Field Notes](DEPLOYMENT_FIELD_NOTES.md) for the observed platform issues, workarounds, and recommended improvements.

## Related submission documents

- [Problem Statement](PROBLEM_STATEMENT.md) : business context, problem, proposed agent, value hypothesis, and scope.
- [Deployment Field Notes](DEPLOYMENT_FIELD_NOTES.md) : issues encountered, evidence, diagnoses, mitigations, and product feedback.
- [Go-Live Note](GO_LIVE_NOTE.md) : operational handover and requirements before serving real customers.
- [`SKILL.md`](SKILL.md) : main skill instructions for Layla Orders.
- [`references/`](references/) : supporting business context, order status, identity, and escalation policies.

These relative links work when the files are committed at the paths shown in the repository structure. If you keep the Chord skill files only inside Chord rather than in Git, remove or update the corresponding repository links and directory entries so the README reflects the actual repository contents.

## External references

- [Chord API documentation](https://api.chordhq.xyz/docs)
- [Chord workspace](https://www.chordhq.xyz/login)
- [Paystack Dashboard](https://dashboard.paystack.com)
- [Paystack API documentation](https://paystack.com/docs/api/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Railway documentation](https://docs.railway.com/)

## Use of AI

AI assistance was used to draft and review parts of the FastAPI service, synthetic fixtures, Chord skill files, debugging notes, and documentation.

The implementation and tool behaviour were checked against direct API responses and observed Chord, Railway, and Paystack test-mode behaviour. AI-generated suggestions were not treated as evidence by themselves; diagnoses were retained only where testing supported them.

The Chord teammate itself was configured in Chord. The skill files were uploaded through the Chord interface, and external tools were registered through Chord's Custom API configuration.

## Project status

**Status: prototype for the TSG Labs build exercise.**

The project demonstrates an order lookup and payment-assurance workflow with external tool calls and explicit failure handling. It is not production-ready. Do not use it to manage real orders, process live payments, or store real customer information until the security, persistence, payment-verification, monitoring, and operational requirements above have been implemented and tested.