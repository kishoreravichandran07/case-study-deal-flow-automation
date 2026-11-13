"""Offline deal-workflow simulator with invented events and rules.

Run python3 example.py. No Airtable/email connector and no outgoing messages.
This is new portfolio work, not original Plug and Play code or configuration.
"""
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Invented, deliberately narrow transitions. Not historical company rules.
RULES = {
    ('screening', 'meeting_completed'): ('diligence', 'Request diligence materials'),
    ('diligence', 'review_completed'): ('committee', 'Prepare committee review'),
}


def apply_event(state, event):
    """Apply one structured event atomically to a copied local state.

    Only events linked to a known deal/thread and matching the current stage
    can advance it. Event IDs are unique within this synthetic event source.
    Replaying an applied event does not emit another prompt.
    """
    result = deepcopy(state)
    if event['id'] in result['processed']:
        return result, {'id': event['id'], 'outcome': 'duplicate'}
    deal = result['deals'].get(event['deal_id'])
    if not deal or event['thread_id'] != deal['thread_id']:
        return result, {'id': event['id'], 'outcome': 'quarantined', 'reason': 'unlinked deal/thread'}
    try:
        timestamp = datetime.fromisoformat(event['at'])
        previous = datetime.fromisoformat(deal['updated_at'])
        if timestamp.tzinfo is None or previous.tzinfo is None:
            raise ValueError('Timezone required')
        stale = timestamp <= previous
    except (ValueError, TypeError):
        return result, {'id': event['id'], 'outcome': 'quarantined', 'reason': 'invalid timestamp'}
    if stale:
        return result, {'id': event['id'], 'outcome': 'quarantined', 'reason': 'stale event'}
    transition = RULES.get((deal['stage'], event['type']))
    if transition is None:
        return result, {'id': event['id'], 'outcome': 'quarantined', 'reason': 'no allowed transition'}
    old = deal['stage']
    deal['stage'], next_step = transition
    deal['updated_at'] = event['at']
    result['processed'].append(event['id'])
    result['prompts'].append({'deal_id': event['deal_id'], 'owner': deal['owner'],
                              'text': next_step, 'event_id': event['id']})
    return result, {'id': event['id'], 'outcome': 'advanced', 'from': old, 'to': deal['stage']}


def replay(data):
    state, audit = deepcopy(data['initial_state']), []
    for event in data['events']:
        state, record = apply_event(state, event)
        audit.append(record)
    return {'state': state, 'audit': audit}


if __name__ == '__main__':
    print(json.dumps(replay(json.loads((HERE / 'synthetic.json').read_text())), indent=2))
