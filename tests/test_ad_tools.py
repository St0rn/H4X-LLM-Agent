import unittest
from ad_tools import check_host, check_domain, discover, ldap_base

class TestAdTools(unittest.TestCase):
    def test_ip_or_dns(self):
        self.assertEqual(check_host('192.0.2.15'), '192.0.2.15')
        self.assertEqual(check_host('dc.example.test'), 'dc.example.test')
        self.assertRaises(ValueError, check_host, 'dc.example.test;id')

    def test_bounded_commands(self):
        probes=discover('192.0.2.15','example.test')
        self.assertEqual(len(probes),6)
        self.assertIn('-sT', probes[3].command)
        self.assertIn('-s base', ldap_base('192.0.2.15','DC=example,DC=test').command)

    def test_refuse_invalid_base(self):
        self.assertRaises(ValueError,ldap_base,'localhost','DC=x;rm -rf /')

if __name__ == '__main__': unittest.main()
