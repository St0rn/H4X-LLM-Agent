# H4X // LLM Agent

**Local AI-assisted security workflow for Kali Linux and Metasploit — powered by Ollama and Model Context Protocol (MCP).**  
**Agent IA local pour Kali Linux et Metasploit — avec Ollama et Model Context Protocol (MCP).**

![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Python 3](https://img.shields.io/badge/Python-3-blue) ![Kali Linux](https://img.shields.io/badge/platform-Kali%20Linux-cyan) ![Status](https://img.shields.io/badge/status-experimental-orange)

**Author / Auteur:** [St0rn](https://github.com/St0rn) — [Cybersecur'IT](https://www.cybersecurit.fr)

[English](#english) · [Français](#français) · [Security](SECURITY.md) · [MIT License](LICENSE)

## English

### Overview

H4X is a terminal-first LLM agent that connects **Ollama** to **Kali MCP Server** and **MetasploitMCP**, discovers their exposed tool schemas, and provides a conversational interface for authorized laboratory tasks. This project is experimental; the language model may select incorrect tools and output must be verified.

### Features

- MCP tool discovery and task-specific tool selection, with an explicit Nmap request parser.
- Kali command previews, structured stdout/stderr and colored execution status.
- Metasploit RPC startup through `hax.sh`, with credentials stored locally outside version control.
- Bounded, unauthenticated AD discovery (`/ad`) and LDAP RootDSE/base queries (`/ldap`).
- Tool-schema technical RAG and optional local `--help` indexing; `.md`, `.txt`, `.rst` and `.log` references.
- Persistent notes, terminal history, `/clear`, and Markdown rendering with Rich.
- Operator confirmation for sensitive tool calls; exact-target automatic Nmap rules.

### Prerequisites

Kali Linux with `mcp-kali-server`, `metasploitmcp`, Metasploit Framework, PostgreSQL, Ollama, Python 3 and a model that supports tool calling. Both MCP packages and their command-line entry points must be available. Prefer an isolated VM snapshot and validate any version-specific CLI differences.

### Install and run

```bash
sudo apt update
sudo apt install -y mcp-kali-server metasploitmcp python3-venv
# Install Ollama from its official documentation before proceeding.
ollama pull qwen2.5:7b
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
chmod +x hax.sh
sudo bash ./hax.sh
```

The launcher starts/checks PostgreSQL, Ollama, Metasploit RPC and the Kali MCP API, then runs `agent.py`. It is designed for a dedicated Kali VM and **requires root** in its current implementation. `H4X_AUTO_TARGETS` defaults to loopback for the public version; edit the scoped host list in `hax.sh` for explicitly authorized targets. Do not put production credentials into the repository.

### Commands

| Command | Function |
|---|---|
| `/help`, `/tools` | Help and discovered MCP tools |
| `/ad <IP-or-FQDN> [domain]` | Bounded AD network, RootDSE and anonymous SMB checks |
| `/ldap <IP-or-FQDN> [baseDN]` | LDAP RootDSE or base-scope query |
| `/inventory [ad\|impacket\|web]` | Installed binary inventory |
| `/toolhelp <binary>` | Index local help for a known executable |
| `/rag tools`, `/rag build`, `/rag search <query>`, `/rag reload` | Technical RAG and document search |
| `/remember <text>`, `/memories`, `/forget <id>` | Persistent notes |
| `/clear`, `/reset`, `/quit` | Clear display, reset context, exit |
| `/format auto\|plain\|markdown` | Response rendering mode |
| `/verbose on\|off`, `/debug` | Command preview and diagnostics |

Use ↑/↓ to navigate command history and ←/→ to edit a line. Local state is stored under `data/`; logs go to `logs/`. Neither should be committed.

### Limitations

- MCP server versions and Metasploit RPC startup differ between Kali releases.
- The RAG is keyword/lexical, not a semantic vector index.
- No real-world integration test or live scanning evidence is claimed here.
- Having an MCP tool exposed does not guarantee the underlying Kali binary is installed.
- A command preview is reconstructed from MCP arguments and may differ from the exact underlying process command.

---

## Français

### Présentation

H4X est un agent LLM en terminal qui relie **Ollama**, **Kali MCP Server** et **MetasploitMCP**. Il découvre les fonctions disponibles, oriente les demandes vers les outils pertinents et permet d'analyser leurs sorties pour des laboratoires et audits explicitement autorisés. Le projet est expérimental : vérifie les arguments et les résultats du modèle.

### Fonctionnalités

- Découverte des fonctions MCP et routage selon la demande, avec reconnaissance explicite des scans Nmap.
- Aperçu des commandes, sorties `stdout`/`stderr` structurées et affichage coloré.
- Démarrage de Metasploit RPC dans `hax.sh`, avec secret local exclu de Git.
- Reconnaissance Active Directory anonyme bornée avec `/ad` et recherches LDAP ciblées avec `/ldap`.
- RAG technique fondé sur les schémas MCP réels, les aides locales `--help` et les documents personnels.
- Notes persistantes, historique au clavier, `/clear` et rendu Markdown avec Rich.
- Confirmation des opérations sensibles, exécution automatique Nmap limitée aux cibles définies.

### Prérequis et installation

Sur une **VM Kali Linux isolée**, installe les paquets `mcp-kali-server`, `metasploitmcp`, PostgreSQL, Metasploit, Python et Ollama. Télécharge un modèle compatible avec les appels d'outils. Ensuite :

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
chmod +x hax.sh
sudo bash ./hax.sh
```

Le script démarre ou contrôle les services, initialise RPC et lance l'agent. Dans cette version, il **nécessite root**. Les cibles Nmap automatiques sont limitées à `localhost`, `127.0.0.1` et `::1` par défaut dans le paquet public. Pour un autre périmètre autorisé, adapte `H4X_AUTO_TARGETS` dans `hax.sh`.

### Commandes

Les commandes sont communes aux deux langues ; consulte le tableau anglais ci-dessus. Exemples :

```text
/tools
/ad 192.0.2.10 lab.example
/ldap dc.lab.example
/rag build
/rag search kerberos
/toolhelp nmap
/remember My lab uses a dedicated, isolated test network
/memories
/clear
```

L'historique des commandes et les notes survivent au redémarrage. `/reset` efface uniquement le contexte conversationnel actif et `/clear` efface uniquement l'écran.

### Limites

- Cette publication ne prétend pas être validée sur une Kali réelle de bout en bout.
- Le RAG effectue une recherche lexicale, pas une recherche vectorielle sémantique.
- Les commandes de diagnostics dépendent des exécutables installés.
- Les aperçus sont reconstruits depuis les paramètres MCP et ne sont pas des preuves de leur exécution.
- Préserve les secrets RPC, les journaux et la mémoire hors du dépôt public.

---

## License / Licence

MIT — see [LICENSE](LICENSE).  
MIT — voir [LICENSE](LICENSE).

**St0rn — https://www.cybersecurit.fr**
