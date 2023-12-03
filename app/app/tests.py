"""
Sample Tests
"""
from django.test import SimpleTestCase

from app import calc

class CalcTest(SimpleTestCase):
  """Test the Calc Module"""

  def test_add_two_numbers(self):
    """Test Add two numbers"""
    result = calc.add(5,6)
    self.assertEqual(result, 11)

  def test_subtract_numbers(self):
    """Test Subtract Numbers"""
    res = calc.subtract(10,15)
    self.assertEquals(res, -5)