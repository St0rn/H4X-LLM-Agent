"""Checks for discovery-first model routing and read-only MCP policy."""
import json
import unittest
from agent import choose_tools, compact_catalog_for_llm, is_read_only_tool, validate_architecture


class CatalogueWorkflowTests(unittest.TestCase):
    @staticmethod
    def available():
        names = ["metasploit__list_payloads", "metasploit__generate_payload",
                 "metasploit__list_jobs", "metasploit__start_handler",
                 "kali__server_health"]
        return [{"type": "function", "function": {"name": n, "parameters": {}}} for n in names]

    def test_discovery_route(self):
        chosen = choose_tools("Metasploit, vérifie la disponibilité d'un payload x64", self.available())
        names = [x["function"]["name"] for x in chosen]
        self.assertIn("metasploit__list_payloads", names)
        self.assertIn("metasploit__generate_payload", names)
        self.assertNotIn("metasploit__start_handler", names)

    def test_readonly_catalog(self):
        self.assertTrue(is_read_only_tool("metasploit", "list_payloads"))
        self.assertTrue(is_read_only_tool("metasploit", "list_jobs"))
        self.assertFalse(is_read_only_tool("metasploit", "generate_payload"))
        self.assertFalse(is_read_only_tool("metasploit", "start_handler"))

    def test_compact_catalog_partial(self):
        items = [f"example/module/{i:03d}" for i in range(100)]
        items[95] = "example/x64/matching_service"
        data = json.loads(compact_catalog_for_llm(items, "x64 matching service", limit=8))
        self.assertEqual(data["returned_entries"], 100)
        self.assertEqual(len(data["matching_entries"]), 8)
        self.assertEqual(data["matching_entries"][0], "example/x64/matching_service")
        self.assertIn("NE PROUVE PAS", data["partial_catalog_warning"])

    def test_no_catalog_false_negative(self):
        items = ["example/other"] * 100
        content = compact_catalog_for_llm(items, "missing", limit=4)
        self.assertIn("limitée", content)

    def test_architecture_still_guarded(self):
        error = validate_architecture("Windows x64", "metasploit", "generate_payload",
                                      {"payload_type": "windows/example"})
        self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()
