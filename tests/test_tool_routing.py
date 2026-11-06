"""Regression tests for deterministic Nmap requests and authorized auto scan."""
import unittest
from unittest.mock import patch
from agent import explicit_nmap_arguments, safe_automatic


class RoutingTests(unittest.TestCase):
    def test_aggressive_quick_scan(self):
        args = explicit_nmap_arguments('fait un scan nmap rapide en Agressif sur www.cybersecurit.fr')
        self.assertEqual(args['scan_type'], '-F -A')
        with patch.dict('os.environ', {'H4X_AUTO_TARGETS':'www.cybersecurit.fr,cybersecurit.fr'}):
            self.assertTrue(safe_automatic('kali','nmap_scan',args))

    def test_no_exec_for_unknown(self):
        args = explicit_nmap_arguments('fais un scan nmap rapide en agressif sur example.org')
        with patch.dict('os.environ', {'H4X_AUTO_TARGETS':'cybersecurit.fr'}):
            self.assertFalse(safe_automatic('kali','nmap_scan',args))

    def test_not_a_scan_request(self):
        self.assertIsNone(explicit_nmap_arguments('Peux-tu expliquer nmap -A ?'))

    def test_no_extra_scripts_auto(self):
        self.assertFalse(safe_automatic('kali','nmap_scan',{
            'target':'127.0.0.1', 'scan_type':'-F -A',
            'additional_args':'--script vuln', 'ports':''}))


if __name__ == '__main__':
    unittest.main()
