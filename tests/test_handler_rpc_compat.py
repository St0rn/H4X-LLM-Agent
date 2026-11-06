"""Tests for x64 handler validation and fail-closed RPC compatibility patch."""
import unittest
from agent import validate_architecture
from tools.patch_metasploitmcp_handler import OLD, patch_source


class HandlerCompatibilityTests(unittest.TestCase):
    def test_listener_rejects_x86_module_for_x64_request(self):
        self.assertIsNotNone(validate_architecture(
            "Windows 64 bits", "metasploit", "start_listener",
            {"payload_type": "windows/meterpreter/reverse_https"}))

    def test_listener_accepts_explicit_x64(self):
        self.assertIsNone(validate_architecture(
            "Windows x64", "metasploit", "start_listener",
            {"payload_type": "windows/x64/meterpreter/reverse_https"}))

    def test_handler_architecture_is_not_checked_for_job_listing(self):
        self.assertIsNone(validate_architecture("Windows x64", "metasploit", "list_jobs", {}))

    def test_patcher_uses_exact_source_signature(self):
        patched, status = patch_source("async def example():\n    " + OLD + "\n")
        self.assertEqual(status, "patch-ready")
        self.assertIn("H4X COMPAT: handler only", patched)
        again, status2 = patch_source(patched)
        self.assertEqual(status2, "already-patched")
        self.assertEqual(again, patched)

    def test_unknown_source_not_modified(self):
        with self.assertRaises(ValueError):
            patch_source("async def example(): pass\n")


if __name__ == "__main__":
    unittest.main()
