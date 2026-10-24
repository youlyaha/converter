import unittest

from converter_tkinter import decimal_to_base, convert_text


class ConverterTests(unittest.TestCase):
    def test_binary(self):
        self.assertEqual(decimal_to_base(10, 2), "1010")

    def test_hex(self):
        self.assertEqual(decimal_to_base(255, 16), "FF")

    def test_octal(self):
        self.assertEqual(decimal_to_base(100, 8), "144")

    def test_ternary(self):
        self.assertEqual(decimal_to_base(42, 3), "1120")

    def test_zero(self):
        self.assertEqual(decimal_to_base(0, 2), "0")

    def test_negative(self):
        self.assertEqual(decimal_to_base(-15, 16), "-F")

    def test_invalid_base(self):
        for base in (1, 17):
            with self.subTest(base=base), self.assertRaises(ValueError):
                decimal_to_base(10, base)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            convert_text("", 2)

    def test_non_integer(self):
        with self.assertRaises(ValueError):
            convert_text("abc", 2)


if __name__ == "__main__":
    unittest.main()
