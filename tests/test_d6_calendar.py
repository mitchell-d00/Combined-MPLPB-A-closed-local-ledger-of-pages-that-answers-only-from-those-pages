"""Source-bound calendar arithmetic over the native D6 entry point."""
from html import escape
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.d6 import SCHEMA, compile_plan, render
from mplpb_combined.ledger import write


def field(label, record='TIDE-4'):
    return {'record_id': record, 'field': label}


def interval(mode, left='Opening Date', right='Closing Date'):
    return {'op': 'day_difference', 'left': field(left), 'right': field(right),
            'calendar': 'proleptic_gregorian', 'mode': mode}


def months(date, amount, overflow):
    return {'op': 'add_months', 'anchor': field(date), 'months': amount, 'overflow': overflow,
            'calendar': 'proleptic_gregorian'}


def relative(base, expression):
    return {'op': 'relative_date', 'anchor': field(base), 'relative': field(expression),
            'calendar': 'proleptic_gregorian'}


class CalendarTests(unittest.TestCase):
    def check(self, body, *steps):
        with TemporaryDirectory() as root:
            text = 'Record-ID: TIDE-4\n' + body
            write(root, title='Dated tide observations', scope='Calendar controls', doc_id='REGISTER-1',
                  body_html='<pre>' + escape(text) + '</pre>', when='2026-11-23')
            return compile_plan(root, {'schema': SCHEMA, 'steps': list(steps)})

    def test_elapsed_and_inclusive_show_different_counts(self):
        result = self.check('Opening Date: March 3, 1898\nClosing Date: March 10, 1898',
                            interval('elapsed'), interval('inclusive'))
        self.assertTrue(result['answer_supported'])
        self.assertEqual([s['value'] for s in result['compiled']['steps']], [7, 8])
        self.assertIn('March 3, 1898', render(result))
        self.assertIn('inclusive', render(result))
        self.assertFalse(result['truth_verified'])

    def test_leap_and_reverse_are_explicit(self):
        result = self.check('Opening Date: Feb 28 1904\nClosing Date: 1904-03-01',
                            interval('elapsed'), interval('elapsed', 'Closing Date', 'Opening Date'),
                            interval('inclusive', 'Opening Date', 'Opening Date'))
        self.assertEqual([s['value'] for s in result['compiled']['steps']], [2, -2, 1])
        result = self.check('Opening Date: 1900-03-01\nClosing Date: 1900-02-28', interval('inclusive'))
        self.assertFalse(result['answer_supported'])

    def test_incomplete_or_non_date_field_stays_unresolved(self):
        for opening in ('1904', 'February 29, 1900', 'February 30, 1904'):
            result = self.check(f'Opening Date: {opening}\nClosing Date: 1904-03-01', interval('elapsed'))
            self.assertFalse(result['answer_supported'])
        result = self.check('Opening Date: 1904-02-28\nClosure Year: 1904', interval('elapsed', right='Closure Year'))
        self.assertFalse(result['answer_supported'])

    def test_month_rule_can_clamp_or_reject(self):
        body = 'Opening Date: 1904-01-31'
        result = self.check(body, months('Opening Date', 1, 'clamp'), months('Opening Date', -1, 'reject'))
        self.assertEqual([s['value'] for s in result['compiled']['steps']], ['1904-02-29', '1903-12-31'])
        self.assertFalse(self.check(body, months('Opening Date', 1, 'reject'))['answer_supported'])

    def test_relative_anchor_requires_matching_declared_role(self):
        body = ('Opening Date: 1904-02-28\nOpening Relative Date: the following day\n'
                'Publication Date: 1904-05-23')
        result = self.check(body, relative('Opening Date', 'Opening Relative Date'))
        self.assertTrue(result['answer_supported'])
        self.assertEqual(result['compiled']['steps'][0]['value'], '1904-02-29')
        self.assertEqual(len(result['evidence']), 2)
        self.assertFalse(self.check(body, relative('Publication Date', 'Opening Relative Date'))['answer_supported'])

    def test_overflow_and_unsupported_relative_syntax(self):
        for body, plan in [
            ('Opening Date: 9999-12-31', months('Opening Date', 1, 'clamp')),
            ('Opening Date: 9999-12-31\nOpening Relative Date: the following day',
             relative('Opening Date', 'Opening Relative Date')),
            ('Opening Date: 1904-03-01\nOpening Relative Date: the following week',
             relative('Opening Date', 'Opening Relative Date')),
        ]:
            self.assertFalse(self.check(body, plan)['answer_supported'])

    def test_calendar_policy_is_required(self):
        for update in ({'calendar': 'julian'}, {'mode': 'business_days'}):
            with self.assertRaisesRegex(ValueError, '(?i)calendar|count'):
                self.check('Opening Date: 1904-01-01', {**interval('elapsed'), **update})
