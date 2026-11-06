"""Regression tests for MCP application errors and architecture mismatch."""
import unittest
from agent import tool_failed, validate_architecture


class RpcErrorHandlingTests(unittest.TestCase):
    def test_mcp_application_error(self):
        self.assertTrue(tool_failed({"status": "error", "message": "missing payload"}))

    def test_transport_error(self):
        self.assertTrue(tool_failed({"message": "connection lost"}, True))

    def test_success(self):
        self.assertFalse(tool_failed({"status": "success", "message": "ready"}))

    def test_nested_result(self):
        self.assertTrue(tool_failed({"result": {"status": "failed"}}))

    def test_x64_mismatch(self):
        self.assertIsNotNone(validate_architecture(
            "windows 64 bits", "metasploit", "generate_payload",
            {"payload_type": "windows/meterpreter/reverse_https"}))

    def test_x64_consistent(self):
        self.assertIsNone(validate_architecture(
            "windows x64", "metasploit", "generate_payload",
            {"payload_type": "windows/x64/meterpreter/reverse_https"}))

    def test_unrelated_tool(self):
        self.assertIsNone(validate_architecture("windows x64", "kali", "server_health", {}))


if __name__ == "__main__":
    unittest.main()
