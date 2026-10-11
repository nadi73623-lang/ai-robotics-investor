import unittest
import scanner
class Tests(unittest.TestCase):
 def test_alias(self):
  self.assertTrue(scanner.matches('Broadcom expands AI networking', 'AVGO','Broadcom'))
  self.assertFalse(scanner.matches('AI changes everything', 'AI','C3.ai'))
 def test_universe(self):
  self.assertEqual(len(set(x[0] for x in scanner.UNIVERSE)),len(scanner.UNIVERSE))
if __name__=='__main__': unittest.main()
