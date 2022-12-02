# import the package
import unittest

from legacyman_parser.hello import greet


class TestHello(unittest.TestCase):

    def test_hello(self):
        self.assertEqual(greet(), 'Hello, world!')


if __name__ == '__main__':
    unittest.main()
