"""
End-to-End API Test Suite for Flask Server
Tests all endpoints (/api/samples, /api/grammar, /api/analyze)
"""

import sys
import os
import json
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import app
from samples import SAMPLE_PROGRAMS


class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        res = self.app.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Automated Syntax and Semantic Analysis System", res.data)

    def test_grammar_endpoint(self):
        res = self.app.get("/api/grammar")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["language_name"], "MiniLang")
        self.assertIn("ebnf", data)
        self.assertIn("operators", data)

    def test_samples_endpoint(self):
        res = self.app.get("/api/samples")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["samples"]), len(SAMPLE_PROGRAMS))

    def test_analyze_empty_code(self):
        res = self.app.post("/api/analyze", json={"code": ""})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "EMPTY_CODE")

    def test_analyze_valid_samples(self):
        for sample in SAMPLE_PROGRAMS:
            if sample["category"].startswith("Valid"):
                res = self.app.post("/api/analyze", json={"code": sample["code"]})
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "SUCCESS", f"Sample {sample['id']} failed: {data}")
                self.assertEqual(data["phase_status"]["lexical"], "PASSED")
                self.assertEqual(data["phase_status"]["syntax"], "PASSED")
                self.assertEqual(data["phase_status"]["semantic"], "PASSED")
                self.assertGreater(data["summary"]["token_count"], 0)
                self.assertGreater(data["summary"]["ast_node_count"], 0)
                self.assertGreater(data["summary"]["symbol_count"], 0)

    def test_analyze_invalid_samples(self):
        for sample in SAMPLE_PROGRAMS:
            if not sample["category"].startswith("Valid"):
                res = self.app.post("/api/analyze", json={"code": sample["code"]})
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data["status"], "ERRORS_DETECTED", f"Sample {sample['id']} was expected to fail")
                self.assertGreater(data["summary"]["total_errors"], 0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFlaskAPI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
