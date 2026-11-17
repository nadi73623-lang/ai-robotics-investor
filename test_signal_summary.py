import unittest
from scanner import summarize_signals

class SignalSummaryTests(unittest.TestCase):
    def test_counts_only_authorized_buy(self):
        rows=[
            {"signal":"BUY","buy_eligible":True,"investment_decision":{"signal":"BUY","buy_eligible":True}},
            {"signal":"BUY","buy_eligible":False,"investment_decision":{"signal":"BUY","buy_eligible":False}},
            {"signal":"WATCH","buy_eligible":False,"early_buy_watch":True,"entry_trigger":{"active":False},"investment_decision":{"signal":"WATCH","buy_eligible":False}},
            {"signal":"WATCH","buy_eligible":False,"early_buy_watch":False,"entry_trigger":{"active":True},"investment_decision":{"signal":"WATCH","buy_eligible":False}},
        ]
        out=summarize_signals(rows)
        self.assertEqual(out,{"buy":1,"early_entry_watch":1,"active_technical_trigger":1,"watch":2,"blocked":3})
    def test_empty_universe(self):
        self.assertEqual(summarize_signals([]),{"buy":0,"early_entry_watch":0,"active_technical_trigger":0,"watch":0,"blocked":0})

if __name__=="__main__": unittest.main()
