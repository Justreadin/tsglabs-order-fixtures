# Role Preference and Problem Statement

**Role preference:** Technical Product Management

## The business

Pepperleaf Kitchen is a small Lagos food vendor that takes advance orders for catering, office lunches and events through WhatsApp. Customers order at least 48 hours before their event and pay in advance. After payment, the vendor sources ingredients, often combining orders into bulk purchases, prepares the food and arranges delivery around the event date.

## The problem

Between payment and delivery, customers have limited visibility into what is happening with their orders. The vendor knows whether an order is awaiting ingredients, being prepared or ready for delivery, but customers often see only that they have paid. This gap drives repetitive “I've paid, where is my order?” messages, particularly during event week, when the vendor has the least time to respond.

Payment discrepancies create a more serious problem: the vendor may be unable to reconcile a customer's claim with the payment record while ingredients and fulfilment decisions are already in motion. The result is wasted time, avoidable uncertainty and potential damage to customer trust.

## What the agent does

Layla Orders is a WhatsApp order-assurance assistant that connects the customer conversation to the order record and Paystack. It verifies the customer's order number and ordering phone number, then checks that the payment transaction is successful and that its reference, amount and currency match the order. The payment reference must be linked to that specific order.

When verification succeeds, Layla updates the order record and reports its current status, event date and recorded delivery window. When payment fails, is short or cannot be verified, it refuses to confirm payment and escalates the issue to the vendor.

**Initial scope excludes** accepting new orders, quoting prices, collecting payments, processing refunds, changing event dates or dietary requirements, and offering discounts. These remain under the vendor's control.

## Why it is worth paying for

The vendor's time during event week is a constrained operational resource. Automating repetitive status checks can return that time to ingredient sourcing, preparation and fulfilment, while more reliable payment verification reduces the risk of false confirmations and unresolved discrepancies. For an event-based business, a failed order can cost more than one sale: it can damage trust, referrals and future bookings.