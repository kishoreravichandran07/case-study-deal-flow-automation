import copy
import json
import unittest
from pathlib import Path
from example import apply_event, replay


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path(__file__).with_name('synthetic.json').read_text())
        self.state = self.data['initial_state']
        self.event = self.data['events'][0]

    def test_allowed_transition_and_prompt(self):
        state, audit = apply_event(self.state, self.event)
        self.assertEqual(state['deals']['D-1']['stage'], 'diligence')
        self.assertEqual(state['prompts'][0]['owner'], 'alex')
        self.assertEqual(audit['outcome'], 'advanced')

    def test_duplicate_idempotency(self):
        state, _ = apply_event(self.state, self.event)
        duplicate, audit = apply_event(state, self.event)
        self.assertEqual(state, duplicate)
        self.assertEqual(audit['outcome'], 'duplicate')

    def test_wrong_thread_does_not_change_state(self):
        event = dict(self.event, thread_id='WRONG')
        state, audit = apply_event(self.state, event)
        self.assertEqual(state, self.state)
        self.assertEqual(audit['outcome'], 'quarantined')

    def test_unknown_deal(self):
        state, audit = apply_event(self.state, dict(self.event, deal_id='D-404'))
        self.assertEqual(state, self.state)
        self.assertEqual(audit['reason'], 'unlinked deal/thread')

    def test_stale_timestamp(self):
        state, audit = apply_event(self.state, dict(self.event, at='2026-10-01T00:00:00+00:00'))
        self.assertEqual(state, self.state)
        self.assertEqual(audit['reason'], 'stale event')

    def test_unrecognized_transition(self):
        state, audit = apply_event(self.state, dict(self.event, type='review_completed'))
        self.assertEqual(state, self.state)
        self.assertEqual(audit['reason'], 'no allowed transition')

    def test_bad_and_naive_timestamps(self):
        for timestamp in ['bad', '2026-11-02T09:00:00']:
            with self.subTest(timestamp=timestamp):
                state, audit = apply_event(self.state, dict(self.event, at=timestamp))
                self.assertEqual(state, self.state)
                self.assertEqual(audit['reason'], 'invalid timestamp')

    def test_full_replay(self):
        out = replay(self.data)
        self.assertEqual(out['state']['deals']['D-1']['stage'], 'committee')
        self.assertEqual(len(out['state']['prompts']), 2)
        self.assertEqual([a['outcome'] for a in out['audit']],
                         ['advanced', 'duplicate', 'quarantined', 'quarantined', 'advanced'])

    def test_no_input_mutation(self):
        original = copy.deepcopy(self.data)
        replay(self.data)
        self.assertEqual(original, self.data)


if __name__ == '__main__':
    unittest.main()
