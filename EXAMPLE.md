# Runnable example: deal-stage automation

New illustrative portfolio work, November 2026. All deals, events, stage rules, and prompts are invented. This is not original Plug and Play code or configuration, and does not claim to reproduce the historical workflow. The historical case study remains in README.md.

## Run locally

Python 3.10 or newer. No packages, account, network connection, or credentials needed.

```sh
python3 example.py
python3 -m unittest test_example.py -v
```

Run these commands from this repository's root. The first command reads synthetic.json and prints JSON without changing files or sending messages.

## What it demonstrates

- Structured synthetic email-thread events link to known deal/thread pairs.
- Explicit state transitions move screening to diligence, then to committee.
- Each accepted event creates a local next-step prompt for the deal owner.
- Duplicate accepted event IDs do not create duplicate stage updates or prompts.
- Unknown deals, wrong threads, stale events, and unsupported transitions are quarantined in the audit output.
- State is copied before processing so the caller's input is not changed.

Expected result: Fictional Orbit ends at committee with two local prompts. The five fixture events produce advanced, duplicate, quarantined, quarantined, advanced. Nine tests cover transitions, replay safety, linkage, timestamps, and input immutability.

## Limits

This is a local simulator, not an Airtable integration or an email parser. Event types are supplied explicitly, not inferred from email language. No email, Airtable record, calendar event, or real deal is changed. Thread IDs are routing checks, not proof of sender identity or authority. Idempotency applies only to accepted event IDs in the supplied state, within one synthetic event source; there is no persistent multi-user database or concurrency protection. Quarantined events are not stored as processed and may be reviewed again. It does not model investment approval or automate investment decisions. Schema validation, real credentials, service permissions, retries, durable storage, and deployment are outside this example. Do not supply real deal data.
