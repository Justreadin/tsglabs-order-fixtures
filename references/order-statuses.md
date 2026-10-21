# Order statuses and payment handling

The order record has an order_status field and a payment reference. Verify the
payment before saying anything about it. The verified amount must equal the
amount due; if it does not, treat it as unconfirmed.

## Order status wording

| order_status | What it means | What you tell the customer |
|---|---|---|
| pending_payment | Order placed, no confirmed payment | "Your payment hasn't been confirmed yet. If you've just paid, it may take a moment — I can check again." |
| paid_awaiting_ingredients | Payment verified, vendor has not sourced ingredients yet | "Your payment is confirmed. Your order is waiting on ingredient sourcing from the supplier." |
| paid_preparing | Payment verified, preparation underway | "Your payment is confirmed. Your order is being prepared." |
| ready_for_dispatch | Prepared, not yet with a rider | "Your payment is confirmed and your order is ready. It's waiting to be dispatched." |
| dispatched | With the rider or courier | "Your payment is confirmed and your order has been dispatched." |
| delivered | Customer confirmed receipt | "Your order was marked as delivered." |
| payment_failed | The payment attempt failed | "Your payment didn't go through. I've flagged this to the vendor so they can help you complete it." |
| payment_abandoned | Payment link opened but not completed | "Your payment wasn't completed. I've flagged this to the vendor so they can send you a fresh payment link." |

## Payment verification results

Verify the payment and compare the result to the order. Handle each case as
follows.

| Verification result | What you do |
|---|---|
| success AND amount matches amount due | Confirm payment. If order_status is pending_payment, update it to paid_awaiting_ingredients and record the verified amount. Tell the customer the verified status. |
| success BUT amount is less than amount due | Do not confirm. Tell the customer the payment on record does not match the order total and that you have flagged it for the vendor. Escalate. |
| success BUT amount is more than amount due | Do not confirm as complete. Tell the customer the payment on record does not match the order total and that you have flagged it for the vendor. Escalate. |
| failed | Do not confirm. Use the payment_failed wording and escalate. |
| abandoned | Do not confirm. Use the payment_abandoned wording and escalate. |
| pending, ongoing, processing, or queued | Do not confirm yet. Tell the customer the payment is still being confirmed and escalate if it has been more than 24 hours since the order was placed. |
| reversed | Do not confirm. Tell the customer the payment was reversed and escalate immediately. |
| verification error, timeout, or no response | Never claim paid. Tell the customer you cannot confirm the payment right now and escalate immediately. |
| the payment response is empty, malformed, or missing the amount or status | Treat as unconfirmed. Never claim paid. Tell the customer you cannot confirm the payment right now and escalate immediately. |

## Delivery windows

The order record may hold a delivery window in two fields:
`delivery_window_start` and `delivery_window_end`. Both are ISO datetimes, or
both are null. A window is the range the vendor has committed to. It is not an
exact arrival time, and it is not the event date.

### How to read the fields

- **Both present:** the delivery date is the date part of `delivery_window_start`.
  The range is the time in `delivery_window_start` to the time in
  `delivery_window_end`. State the date and the range, labelled as the delivery
  window.
- **Either null:** treat the window as not confirmed, and use the not-confirmed
  wording below.
- **The fields are missing from the response entirely:** treat as not confirmed.
- **Never say "no delivery window is recorded" or "a delivery time isn't
  recorded" when both fields hold values.** Read the fields before you answer.
  If they are present, state the window.

### What you tell the customer

| Window on the record | What you tell the customer |
|---|---|
| `delivery_window_start` and `delivery_window_end` both present | "Your delivery is scheduled for [date from delivery_window_start], between [time from delivery_window_start] and [time from delivery_window_end]. That's the window the vendor has committed to; a more exact time isn't confirmed." |
| either field null, or both missing | "A delivery window hasn't been confirmed on this order yet. I've flagged it for the vendor to confirm the delivery time with you." |

### Rules for delivery

- Never convert a window into an exact time. If the customer asks "what time
  exactly?", repeat the window and say a more exact time is not confirmed.
- Never state a delivery time when the window is null.
- Never state or imply that the event date is the delivery date. They are
  separate fields and may differ. Do not infer one from the other.
- If the window's date differs from the event date, state both, clearly labelled:
  "delivery is scheduled for X; your event date is Y."
- Never promise the window is guaranteed. Say "scheduled for" or "the vendor has
  committed to", not "it will arrive at".
- If the customer needs a tighter time than the window, flag it for the vendor.
  Do not negotiate or narrow the window yourself.
- If the customer asks for a delivery time on an order whose status is
  `pending_payment`, do not discuss delivery at all until the payment is
  resolved. Resolve the payment question first.
- If the customer asks about a window on an order that is `payment_failed` or
  `payment_abandoned`, do not discuss delivery. The payment is not complete, so
  no delivery commitment applies.

## Hard rules for this file

- The amount check is not optional. A "success" status with the wrong amount is
  not a confirmed payment.
- If the order record and the payment result disagree, escalate. Do not pick one.
- Never include payment references, transaction IDs, amounts paid, or the raw
  verification result in a customer reply. Describe the outcome in the wording
  above, nothing more.
- You may state the event date and the delivery window from the record. You may
  not state an exact delivery time, a preparation start time, or a rider arrival
  time.
- If a field is not in the response, say you do not have that information. Do not
  substitute a different field, and do not reuse wording from the null case.