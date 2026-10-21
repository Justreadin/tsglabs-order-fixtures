# Go-Live Note: Pepperleaf Kitchen

**Product:** Layla Orders  
**Audience:** Pepperleaf Kitchen owner and day-to-day operator  
**Purpose:** Explain what the assistant does, what remains under the owner's control, and what must be completed before real customers use it.

## 1. What Layla Orders does

Layla Orders is a WhatsApp assistant that answers a common customer question: **“I've paid. Where is my order?”**

It checks the order record and verifies payment against Paystack before confirming that a payment has been received. When the payment checks out, it updates the order record so the status stays accurate.

Layla must not tell a customer that a payment is confirmed unless verification has succeeded and the verified amount matches the order total.

## 2. What it can do

- **Verify the customer against the order.** The customer must provide the order number and the phone number used when placing the order. Layla does not reveal order details until both match.
- **Verify payment.** It checks the transaction with Paystack and confirms payment only when the verification succeeds and the amount matches the order total.
- **Report order progress.** It tells the customer the recorded order status and event date, and the delivery window if one is set on the order.
- **Update the order record.** When payment is verified, it can move an order from `pending_payment` to `paid_awaiting_ingredients`.
- **Escalate exceptions.** It hands the conversation to the owner when payment fails, the amount is short, payment cannot be verified, or the customer requests a refund or date change or makes a complaint.

## 3. What it does not do

- It does not promise an exact delivery time. It can communicate a delivery window recorded on the order, but it must not invent a commitment. The event date must not be treated as the delivery date.
- It does not quote prices, accept new orders, or take payments. Those remain the owner's responsibilities.
- It does not process refunds, change event dates or dietary requirements, or offer discounts.
- It does not discuss delivery as though an order is confirmed when payment is still pending or has failed.

## 4. Requirements before real customers use it

### Connect and approve a real WhatsApp number

The simulator is for testing; it is not a customer-facing phone number. A real WhatsApp number must be connected to the workspace, and the workspace must be approved for its use before customers can reach the agent.

### Configure live Paystack credentials

Replace test credentials with live Paystack keys, and ensure the keys belong to the same Paystack account that creates the customers' payment links. A key from one account cannot verify a transaction belonging to another account.

Before opening the service to customers, run and verify a controlled live transaction using the intended production setup.

### Bind each payment reference to its order

In the prototype, payment references are seeded in the test data. In production, the reference must be created when the payment link is issued, stored against the specific order, and checked before the order is marked paid.

**This is a critical control.** Without a reliable link between the payment reference and the order, Layla could confirm a transaction that belongs to a different order.

### Set a delivery window for each advance order

If an order has no delivery window, Layla cannot report one. It may be able to state the recorded event date, but that does not answer when delivery is expected.

Set and record the delivery window when confirming each order. This is an operational process the business must follow, not merely a software setting.

### Replace in-memory storage with a persistent database

The prototype stores orders in memory, so records and status changes can be lost when the service restarts or is redeployed.

Before go-live, use a persistent database and maintain an audit trail showing what changed and when.

### Verify that escalation reaches a person

The agent is configured to hand conversations to the owner, but successful notification delivery was not confirmed during testing.

Before go-live:

1. Trigger a test escalation.
2. Confirm that the alert actually reaches the intended phone or email.
3. Decide who is responsible for responding during service hours.
4. Confirm where unresolved and failed escalations can be reviewed.

If nobody monitors the handoff channel, escalation will not reliably resolve customer issues.

### Define the fallback for service outages

If Paystack or the order service is unavailable, Layla should tell the customer that it cannot confirm the information at that moment and flag the issue for the owner. It must not guess.

Confirm where these flags appear and how the owner will identify and handle them.

## 5. What happens when a payment fails

Layla tells the customer that payment has not been confirmed and flags the issue for the owner. It must not tell the customer that the order is paid while the payment issue remains unresolved.

If ingredients have already been purchased, the owner decides whether to hold the order, request payment again, or cancel it. Layla must not make that business decision independently.

## 6. Known limitation: repeat escalations

A conversation can only be escalated once under the current behaviour. If a customer has already been handed to a human and later messages again about a different order in the same thread, another escalation attempt may fail until the conversation is returned to agent handling.

Until this limitation is fixed and retested, the owner should review the agent's conversation list during service hours rather than relying exclusively on escalation alerts.

## 7. Ownership and incident response

Name one person responsible for Layla day to day and one backup. Both should know how to access the Chord workspace, Paystack account, and order service, subject to appropriate access controls.

They should know how to:

- Review conversations and investigate customer issues.
- Check the order record and Paystack verification result.
- Respond to escalations and unresolved payment discrepancies.
- Pause the agent if it begins giving incorrect or unsafe answers.

Pausing the agent is reversible, but the team should know who is authorized to do it and when to use it.

## Go-live decision

**Do not open Layla Orders to real customers until the critical requirements above have been completed and tested**, especially payment-reference binding, live payment verification, persistent order storage, real WhatsApp access, and confirmed human escalation.

The prototype demonstrates the intended workflow, but the remaining controls are necessary to operate it reliably with real customer orders and payments.

The next thing to build is order intake: 
letting a customer start a request before they have paid, so the vendor receives a structured request rather than a series of WhatsApp messages. That would let the agent collect the event date, items, quantity and delivery location, and create a request for you to review and price. It should not quote prices itself. That is a second project, and it should be built only after this one has run in production for a few weeks.