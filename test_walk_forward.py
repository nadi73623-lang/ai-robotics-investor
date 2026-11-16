import unittest
from walk_forward import validate_point_in_time_rows, walk_forward_returns

class WalkForwardTests(unittest.TestCase):
    def row(self):
        return {"ticker":"XYZ","decision_date":"2024-01-02","data_as_of":"2024-01-01","universe_start":"2020-01-01","universe_end":"","entry_price":"10","exit_date":"2024-01-10","exit_price":"11","signal":"BUY"}
    def test_valid_point_in_time_row(self):
        self.assertEqual(validate_point_in_time_rows([self.row()])["status"],"validated")
    def test_lookahead_is_rejected(self):
        row=self.row(); row["data_as_of"]="2024-01-03"
        self.assertEqual(validate_point_in_time_rows([row])["status"],"blocked")
    def test_pre_listing_member_rejected(self):
        row=self.row(); row["universe_start"]="2024-02-01"
        self.assertEqual(validate_point_in_time_rows([row])["status"],"blocked")
    def test_empty_backtest_is_blocked(self):
        self.assertEqual(walk_forward_returns([])["status"],"blocked")

if __name__=="__main__": unittest.main()
