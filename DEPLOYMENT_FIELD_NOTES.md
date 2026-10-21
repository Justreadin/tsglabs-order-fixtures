# Deployment Field Notes

**Project:** Layla Orders  
**Platform:** Chord  
**External systems:** Custom order service hosted on Railway; Paystack test mode  
**Development environment:** Windows with PowerShell  
**API environment:** Chord production API  
**Document purpose:** Record deployment and integration issues, their diagnosis, mitigations, and recommended product improvements.

These notes document problems encountered while building Layla Orders on Chord, connecting it to a self-hosted order service on Railway, and verifying payments against Paystack in test mode. Each entry distinguishes what happened, how the cause was investigated, what was done to mitigate the issue, and what could prevent similar problems for future builders.

## Summary

| # | Issue | Impact | Resolution / mitigation |
|---|---|---|---|
| 1 | Escalation cannot be re-triggered on a thread already in `human_active` | The agent may tell a customer a handoff occurred when the tool call failed | Use a fresh thread for isolated escalation tests; make the agent check thread state and report handoff outcomes accurately |
| 2 | Stale instructions in a skill reference file contradicted delivery-window data | The agent ignored delivery-window fields returned by the API | Updated the business-context and related reference files to match the current data model |
| 3 | Editing a reference file changed the skill instruction entrypoint | Edits to `SKILL.md` appeared ineffective and behaviour became inconsistent | Restored `Tsglabs/SKILL.md` as the instruction entrypoint |
| 4 | Chord Custom API test panel did not reliably send query parameters | A valid endpoint returned a `422` in the panel; an earlier `Status: 0` remained unexplained | Tested the endpoint through `curl` and the agent conversation instead of relying on the panel |
| 5 | WhatsApp Simulator rendered internal reasoning in the customer message bubble | Internal logic and order information appeared in customer-facing output | Used the Chord builder direct line for the demonstration and documented the simulator issue for platform improvement |

---

## 1. Escalation cannot be re-triggered on a thread

### What happened

After an earlier escalation moved a conversation thread to `human_active`, every subsequent escalation attempt on that same thread failed with:

```text
Invalid transition for thread 6ad67e2147ca6a43d858c5d4:
current state 'human_active' cannot move to 'human_active'
(allowed from: [agent_active])
```

The tool call failed, but the agent still told the customer, “I've flagged this for the vendor.” The customer received an assurance that a handover had happened when it had not.

### How the cause was diagnosed

The execution trail showed `handover_to_human` with a failed red marker while the reply text claimed the issue had been flagged. The error identified the current state, target state, and allowed source state. This indicated that escalation is a state transition that cannot be repeated once the thread is already `human_active`.

The consequence is more serious than the tool error itself. If a customer is escalated once and later messages again about a different order, the second issue may not reach a human. The agent may falsely assure the customer that the issue has been flagged, causing the customer to wait for a handoff that did not occur.

### How it was mitigated

A fresh conversation was started for each escalation scenario so that each test thread began in `agent_active`. This was sufficient for isolated escalation tests.

For production, the agent should check the thread state before attempting a handoff and accurately communicate the result. It should say that a human is already handling the thread if that is the current state, or explain that it could not flag the issue if the handoff failed.

### Recommended improvement for Chord

Treat an escalation request on a thread that is already `human_active` as an idempotent success rather than an invalid transition. The objective of escalation is to ensure that a human is handling the conversation; if that is already true, the objective has been met. Returning a successful result with the current state would help the agent continue safely.

If that behaviour is not possible, the handover tool should return a distinct result such as `already_human_active`. The agent could then say, “A person is already handling this,” instead of claiming that it has newly flagged the issue.

---

## 2. A stale instruction in one skill file overrode another

### What happened

The order service returned `delivery_window_start` and `delivery_window_end` for `ORD-201`, but the agent replied, “No delivery window is recorded on the order.”

I edited the delivery section in `references/order-statuses.md` three times and published three versions, but the behaviour did not change. The data was present in the tool response on every attempt.

### How the cause was diagnosed

First, I confirmed the field values with a direct `curl` request to the order service. The response included:

```json
{
  "order_id": "ORD-201",
  "delivery_window_start": "2026-10-23T10:00:00",
  "delivery_window_end": "2026-10-23T13:00:00"
}
```

The service was returning the expected data. I then compared the `Lookup_order` result in the execution trail with the agent's reply. The tool returned the window, but the model did not use it.

The conflicting instruction was in another file: `references/business-context.md`, which the skill loads at the beginning of each turn. It still contained this statement:

> You do not know a delivery time. Only the event date is on the record.

That statement had been accurate before delivery-window fields were added, but it was not updated when the data model changed. The agent read it at the start of every turn, and it contradicted the more specific delivery guidance elsewhere in the skill. Two files contained opposing instructions, and the more absolute wording appeared to dominate.

### How it was fixed

I updated `business-context.md` to describe the delivery window and defer to `order-statuses.md` for how to communicate it. I also updated `identity-rule.md`, which contained a similar stale instruction about multi-order listings, and added a precondition to the delivery-time escalation trigger in `escalation-policy.md`.

After these changes, the agent correctly stated the recorded window: “Delivery is scheduled for 23 October between 10am and 1pm.”

### Recommended improvement for Chord

When a data model changes, every skill file that describes the old model may need to change as well. Chord did not flag the contradiction between the reference files.

A skill-package linting tool could check reference files for statements about fields that are now returned by the connected tool schema. At minimum, the editor could warn when one file says that only the event date is recorded while another file or the tool schema includes delivery-window fields.

**Lesson:** When the agent behaves incorrectly, inspect every instruction and reference file it loads—not only the file most recently edited.

---

## 3. Editing a reference file changed the instruction entrypoint

### What happened

After I edited `references/escalation-policy.md` through the Skills panel, the agent's behaviour changed in ways that did not match the edit. General questions produced a self-audit of previous mistakes, and the delivery rules stopped applying.

The Skills panel showed that the **Instructions** badge had moved from `Tsglabs/SKILL.md` to `Tsglabs/references/escalation-policy.md`.

The instruction entrypoint had changed. The agent was being driven primarily by the escalation policy, while the main skill file which contained the task, workflow, and reply rules was no longer the primary instruction.

### How the cause was diagnosed

The Skills panel displays an **Instructions** badge next to the file serving as the entrypoint. After the edit, that badge appeared beside `escalation-policy.md`. `SKILL.md` instead showed the options **Edit / Make instructions / Remove**, indicating that it was being treated as a reference file.

Eight publishes in fifteen minutes became a visible symptom: repeated fixes to `SKILL.md` had no effect because it was no longer the instruction entrypoint.

### How it was fixed

I used **Make instructions** on `Tsglabs/SKILL.md` to restore it as the entrypoint, then confirmed that the **Instructions** badge had moved back. The next response was correct, and the unexpected self-audit behaviour stopped.

### Recommended improvement for Chord

Warn users when an edit changes the instruction entrypoint, or lock the entrypoint unless a user explicitly changes it. The **Instructions** badge was the only signal, and it was easy to miss while editing file content.

A banner such as “This file is now the instruction entrypoint,” or a confirmation dialog before changing the entrypoint, would help prevent unnecessary publish cycles and confusing test results.

---

## 4. The Custom API test panel did not reliably send query parameters

### What happened

Testing the **Find orders by phone** connection from the Chord admin panel returned:

```text
Status: 422 · 63 ms
{"detail":[{"type":"missing","loc":["query","phone"],"msg":"Field required","input":null}]}
```

The `phone` parameter had been entered in the test form's Parameters row. The same URL with the same query string returned the expected three-order response through `curl`.

On an earlier attempt, the same panel returned `Status: 0` with an empty body and no error detail.

### How the cause was diagnosed

The `422` response came from FastAPI, showing that the request reached the server and that connectivity was working. The error specifically identified the required `phone` query parameter as missing, even though it had been populated in the form.

A direct `curl` request with the same query string succeeded, isolating the reproducible `422` behaviour to the Chord test panel rather than the API endpoint.

The earlier `Status: 0` did not recur, and its cause could not be established. The service was running on a paid Railway plan, so a cold start was not an obvious explanation. The later `422` confirmed that the server was reachable, but the first result remains undiagnosed.

### How it was mitigated

I stopped using the admin test panel for endpoints that require query parameters. Instead, I tested through the conversation, where the agent calls the tool using parameters from the saved connection definition. The endpoint worked through `curl` and the conversation workflow; the admin test form was not reliable for this test.

### Recommended improvements for Chord

1. **Validate required parameters before running a test.** The test panel should prefill query parameters and path variables from the saved connection definition, or disable **Run test** until required values are present.

2. **Represent connection failures distinctly.** `Status: 0` should be presented as a connection failure or timeout, with the resolved URL and diagnostic detail where available. Showing `0` alongside HTTP status codes such as `200` and `422` can misleadingly imply that `0` is an HTTP status code.

3. **Support multi-endpoint API organization.** The Custom API setup treated each endpoint as a separate connection, with no OpenAPI import on the connection form. The **Import OpenAPI** button appeared on the previous page but was not available in the form itself. Three endpoints therefore required three separate forms, without shared identity, joint versioning, or a clear indication that they belonged to one service. A service-level grouping would make multi-endpoint integrations easier to understand and maintain.

---

## 5. WhatsApp Simulator renders internal reasoning in the customer message

### What happened

When testing the agent in the official WhatsApp Simulator (`chat.tsglabs.dev`), the agent's internal reasoning rendered inside the WhatsApp message bubble alongside the customer-facing reply.

For example, in response to a payment verification request, the simulator displayed:

> The payment verified successfully and the amount matches. The order is already in the paid status, so no update is needed. Your payment is confirmed. Your order is waiting on ingredient sourcing...

In a security test where a wrong phone number was provided, the simulator displayed the internal logic evaluating the mismatch including the actual phone number on the order before sending the generic failure message.

Furthermore, when an escalation was triggered in the simulator, the interface became permanently stuck on *“No reply yet. If someone has taken over in Chord, their reply will appear here,”* because the thread was already in a `human_active` state (see Issue 1).

### How the cause was diagnosed

I ran the exact same test prompts in the Chord builder direct line. In the direct line, the internal reasoning was correctly separated into the **How I did this** step trail, and the customer message bubble contained only the sanitized reply.

The skill version, teammate, and tool connections were identical across both tests. This isolated the issue to the simulator's rendering logic and its handling of the conversation state machine.

The finding is based on the observed difference between the two testing surfaces. It does not establish how every production messaging channel renders agent responses, but it demonstrates that the simulator can expose information that was separated correctly in the builder direct line.

### How it was mitigated

I recorded the demonstration entirely from the Chord builder direct line, where the output behaviour matched the intended customer-facing response.

This was a workaround for the evaluation demonstration, not a fix to the WhatsApp Simulator itself.

### Recommended improvement for Chord

1. **Sanitize simulator output.** The simulator should suppress internal reasoning before rendering it in a customer-facing message, or display execution reasoning in a clearly separate, non-customer-visible panel, as the direct line does.

2. **Separate internal execution details from customer-visible output.** Security-sensitive information, such as stored phone numbers and identity-check reasoning, must not appear in the customer message bubble. The interface should clearly distinguish tool traces and internal execution details from the final reply.

3. **Handle escalation failures gracefully.** If an escalation fails because of the thread state, the simulator should surface the error to the agent and allow a fallback response rather than remaining indefinitely in an “operator waiting” state.

**Why this matters:** The issue is more serious than a cosmetic rendering defect. A customer-facing interface that displays internal reasoning can expose sensitive order information and confuse customers about what the agent has actually done. The simulator should reliably represent the intended customer-visible response.

---

## Follow-up work

The following items are proposed next steps, ordered by priority. They are not represented as completed work.

1. **Move payment reconciliation into the order service.** Have the service compare the Paystack verification result with the order's expected reference, amount, and currency, then return a single verified or unverified result. This would reduce reliance on the agent to perform arithmetic and apply critical payment rules.

2. **Enforce identity checks server-side.** Require the ordering phone number on the order-lookup endpoint and wire that requirement into the Chord tool definition. The API currently supports the phone parameter as optional, but it is not yet wired into the Chord tool definition.

3. **Add scoped order intake.** Allow customers to provide order requirements before paying. The initial scope would collect details and create a `pending_vendor_review` record, without pricing, order acceptance, or payment initiation.

4. **Add durable persistence and an audit trail.** Replace in-memory order storage with a persistence layer so status changes survive a redeploy and can be reviewed later.

5. **Retest the final customer-facing surface after platform fixes.** Repeat the identity-mismatch, payment-verification, and escalation scenarios in the WhatsApp Simulator to confirm that internal execution details are not displayed, customer-visible replies are correctly sanitized, and failed handoffs do not leave the interface stuck.

## Closing observations

These issues showed that agent reliability depends on more than the model's response quality. Tool behaviour, state transitions, reference-file consistency, data-model changes, interface rendering, and the accuracy of claims made to customers all matter.

The most important operational lesson is to verify both sides of an interaction: what the agent told the customer and what the connected systems actually did. A successful-looking response is not proof that a tool call succeeded, that a handoff occurred, or that a record changed as intended.

Testing on the final integration surface also matters. The WhatsApp Simulator revealed rendering issues that the builder direct line did not, demonstrating that a successful test in one interface does not establish that another interface presents the same information safely.

For AI product development, this distinction is critical: **the system must not only perform the correct action; it must also report that action accurately and expose only the information intended for the customer.**