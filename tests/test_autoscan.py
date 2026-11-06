import unittest
from unittest.mock import patch
from agent import safe_automatic

class AutoScanTest(unittest.TestCase):
    def test_known_domain(self):
        self.assertTrue(safe_automatic("kali", "nmap_scan", {"target":"fabiendromas.pro", "scan_type":"-F", "additional_args":"-Pn", "ports":""}))
    def test_localhost(self):
        self.assertTrue(safe_automatic("kali", "nmap_scan", {"target":"127.0.0.1", "scan_type":"-sT", "ports":"1-1024"}))
    def test_unknown_domain(self):
        self.assertFalse(safe_automatic("kali", "nmap_scan", {"target":"example.net", "scan_type":"-F"}))
    def test_scripts_not_auto(self):
        self.assertFalse(safe_automatic("kali", "nmap_scan", {"target":"fabiendromas.pro", "scan_type":"-F", "additional_args":"--script vuln"}))
    def test_other_tools_not_auto(self):
        self.assertFalse(safe_automatic("metasploit", "run_exploit", {}))
    def test_extra_authorized_targets(self):
        with patch.dict("os.environ", {"H4X_AUTO_TARGETS":"lab.test"}):
            self.assertTrue(safe_automatic("kali", "nmap_scan", {"target":"lab.test", "scan_type":"-F"}))

if __name__ == "__main__":
    unittest.main()
