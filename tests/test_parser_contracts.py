import unittest

from tools.verify_parser_contracts import verify


class ParserContractTests(unittest.TestCase):
    def test_contracts_pass(self):
        report = verify()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["parser_contracts"]), 2)


if __name__ == "__main__":
    unittest.main()
