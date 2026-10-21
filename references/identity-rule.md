# Identity check

Before revealing any order detail, confirm the customer knows the order.

## What to collect

Ask for both:
1. The order number (for example ORD-201)
2. The phone number used when the order was placed

If the customer gives only one, ask for the other before looking anything up.
Pass both to the order lookup tool. The tool returns the order only when both
match.

## Normalising the phone number

Normalise both the number the customer gives and the number on the order record
to the same form before comparing:
1. Remove all spaces, dashes, brackets and dots.
2. Remove a leading +234, then a leading 234, then a leading 0.
3. Compare the remaining digits exactly.

Examples that must all match a stored value of 7063749513:
- 07063749513
- +2347063749513
- 234 706 374 9513
- 0706-374-9513

## The single failure message

If the order number does not exist, OR the phone number does not match the
record, reply with exactly this message and nothing more:

"I couldn't find an order matching those details. Please check the order number
and the phone number you used when ordering, and send them again. If you're sure
they're correct, I can flag this for the vendor to look into."

Do not vary this message between the two cases. Do not say "that order exists but
the number doesn't match." Do not confirm or deny that an order number exists.
Do not add any note before or after this message.

## Multiple orders on one phone number

If the phone number matches more than one order and the customer gave an order
number, use the order number. If the customer gave only a phone number, list the
order numbers, event dates and delivery windows only, and ask which one they
mean. Do not list amounts, items, or any other detail until the customer picks
one.

## Hard rules for this file

- Never describe the identity check itself to the customer. Do not explain
  normalisation, matching, or why the check failed.
- Never list order numbers from a phone lookup unless the customer supplied that
  phone number in this conversation.
- Never mention a phone number from the order record in a reply.