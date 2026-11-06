"""Bounded, unauthenticated AD discovery via Kali MCP execute_command.

No password collection, ticket extraction, or credential replay is performed.
Targets are validated and all subprocess arguments are shell-quoted.
"""
from __future__ import annotations
import ipaddress
import re
import shlex
from dataclasses import dataclass

HOST = re.compile(r"^(?=.{1,253}$)[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?$", re.ASCII)
BASE = re.compile(r"^(?=.{1,512}$)(?:[A-Za-z][A-Za-z0-9-]*=[A-Za-z0-9_. -]+)(?:,[A-Za-z][A-Za-z0-9-]*=[A-Za-z0-9_. -]+)*$")


def check_host(value: str) -> str:
    value = value.strip().rstrip('.')
    if not value or value.startswith('-') or any(c in value for c in ('/', ':', '\\', ' ')):
        raise ValueError('IP IPv4 ou nom DNS attendu (sans protocole ni port)')
    try:
        ipaddress.IPv4Address(value)
        return value
    except ipaddress.AddressValueError:
        pass
    if not HOST.fullmatch(value) or '..' in value:
        raise ValueError('Cible IP/FQDN invalide')
    return value


def check_domain(value: str) -> str:
    value = check_host(value)
    try:
        ipaddress.ip_address(value)
        raise ValueError('Le domaine doit être un nom DNS, pas une IP')
    except ValueError as exc:
        if str(exc).startswith('Le domaine'):
            raise
    return value


def join(*args: str) -> str:
    return shlex.join(args)


@dataclass(frozen=True)
class Probe:
    title: str
    command: str


def discover(target: str, domain: str | None = None) -> list[Probe]:
    target = check_host(target)
    if domain:
        domain = check_domain(domain)
    probes = [
        Probe('Résolution locale', join('getent', 'ahostsv4', target)),
        Probe('Ports AD courants (TCP)', join('nmap', '-sT', '-Pn', '-n', '--open', '-p',
              '53,88,135,139,389,445,464,636,3268,3269', '--host-timeout', '40s', target)),
        Probe('LDAP RootDSE anonyme', join('ldapsearch', '-x', '-LLL', '-o', 'nettimeout=5',
              '-H', f'ldap://{target}:389', '-s', 'base', '-b', '',
              'defaultNamingContext', 'rootDomainNamingContext', 'dnsHostName',
              'supportedLDAPVersion', 'supportedSASLMechanisms')),
        Probe('SMB : liste anonyme des partages (si autorisée)',
              join('smbclient', '-L', f'//{target}', '-N', '-g', '-t', '5')),
    ]
    if domain:
        probes.insert(0, Probe('SRV contrôleurs de domaine',
                               join('dig', '+time=3', '+tries=1', '+short',
                                    'SRV', f'_ldap._tcp.dc._msdcs.{domain}')))
        probes.insert(1, Probe('SRV Kerberos',
                               join('dig', '+time=3', '+tries=1', '+short',
                                    'SRV', f'_kerberos._tcp.{domain}')))
    return probes


def ldap_rootdse(target: str) -> Probe:
    target = check_host(target)
    return Probe('RootDSE LDAP anonyme', join(
        'ldapsearch', '-x', '-LLL', '-o', 'nettimeout=5',
        '-H', f'ldap://{target}:389', '-s', 'base', '-b', '',
        'namingContexts', 'defaultNamingContext', 'dnsHostName', 'supportedLDAPVersion'))


def ldap_base(target: str, base: str, attribute: str = 'objectClass') -> Probe:
    target = check_host(target)
    if not BASE.fullmatch(base):
        raise ValueError('Base DN invalide : ex. DC=lab,DC=local')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]{0,63}', attribute):
        raise ValueError('Attribut LDAP invalide')
    # Limited to base-scope inspection to avoid directory-wide bulk collection.
    return Probe('LDAP base DN', join('ldapsearch', '-x', '-LLL', '-o', 'nettimeout=5',
                                    '-H', f'ldap://{target}:389', '-s', 'base', '-b', base,
                                    '(objectClass=*)', attribute))
