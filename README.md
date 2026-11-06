<div align="center">

# H4X // LLM AGENT

**LOCAL AI · KALI LINUX · MCP · METASPLOIT · TECHNICAL RAG**

[![MIT License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
![Kali Linux](https://img.shields.io/badge/Platform-Kali%20Linux-557C94?style=for-the-badge&logo=kalilinux&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/AI-Ollama-171717?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Experimental-E8A317?style=for-the-badge)

**An AI-assisted security operations terminal powered by local language models.**  
**Un terminal de cybersécurité assisté par IA, propulsé par des modèles locaux.**

**Author / Auteur:** [St0rn](https://github.com/St0rn) · [Cybersecur'IT](https://www.cybersecurit.fr)

[🇬🇧 English](#english) · [🇫🇷 Français](#français) · [MIT License](LICENSE)

</div>

---

> [!IMPORTANT]
> **EN:** For authorized security assessments and controlled laboratories only. H4X is an experimental, operator-assisted project; review generated commands and verify actual execution results.  
> **FR :** Réservé aux audits explicitement autorisés et aux laboratoires contrôlés. H4X est un projet expérimental piloté par un opérateur ; vérifie les commandes proposées et les résultats réels.

## System architecture / Architecture du système

```text
                        +------------------------+
                        | Operator / Opérateur   |
                        +-----------+------------+
                                    |
                                    v
                        +------------------------+
                        |        H4X CLI         |
                        +-----------+------------+
                                    |
                  +-----------------+------------------+
                  |                 |                  |
                  v                 v                  v
          +---------------+ +---------------+ +----------------+
          | Ollama / LLM  | | Technical RAG | | Local memory   |
          +-------+-------+ +---------------+ +----------------+
                  |
                  v
          +-----------------------+
          | Intent & tool routing |
          +-----------+-----------+
                      |
                      v
          +-----------------------+
          | Authorization policy  |
          | + operator approval   |
          +-----------+-----------+
                      |
              +-------+-------+
              |               |
              v               v
       +-------------+ +----------------+
       |  Kali MCP   | | MetasploitMCP  |
       +------+------+ +-------+--------+
              |                |
              +--------+-------+
                       |
                       v
             +------------------+
             | Tool result / CLI|
             +------------------+
```

---

<a id="english"></a>
# 🇬🇧 English

## Overview

**H4X LLM Agent** integrates a local Ollama model with **Kali MCP Server** and **MetasploitMCP**, providing an interactive security-testing workflow in the terminal. It combines MCP tool discovery, task-aware routing, technical documentation retrieval and persistent operator notes.

H4X is designed to assist an experienced operator, **not** to autonomously certify a system as secure.

### Highlights

| Component | Capability |
|:--|:--|
| **Local inference** | Ollama-based language model orchestration |
| **Kali MCP** | Discover and invoke tools exposed by Kali MCP Server |
| **MetasploitMCP** | Interact with a configured Metasploit RPC instance |
| **Technical RAG** | Search MCP schemas, local command help and project documentation |
| **Tool-aware routing** | Translate explicit requests into tool arguments, including Nmap scan modes |
| **Interactive experience** | Rich terminal output, editable history and command previews |
| **Active Directory** | Bounded AD, DNS, SMB and LDAP discovery helpers |
| **Local memory** | Save and retrieve operator notes across sessions |
| **Operator controls** | Explicit target allowlists and confirmation for sensitive operations |

### Requirements

- Kali Linux, preferably running in an isolated VM
- Python 3 and `venv`
- Ollama and a locally downloaded compatible model
- Kali MCP Server and MetasploitMCP
- Metasploit Framework, RPC and PostgreSQL when using the Metasploit integration

> [!NOTE]
> MCP server package names and startup commands vary between Kali releases. Verify the installed versions and actual server entry points. The current launcher uses elevated privileges and should only run in a dedicated environment.

### Quick start

```bash
git clone https://github.com/St0rn/H4X-LLM-Agent.git
cd H4X-LLM-Agent

python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt

# Install Ollama and configure the two MCP servers beforehand.
ollama pull qwen2.5:7b

chmod +x hax.sh
sudo bash ./hax.sh
```

The launcher checks or starts dependent local services and starts the agent. **Review `hax.sh` before running it as root.** Never add RPC credentials to tracked files.

### Technical RAG

The knowledge layer uses a **lexical index** over available MCP tool names, descriptions and JSON argument schemas. It can also index the `--help` output of installed tools and text-based project documentation. It is not a semantic vector database and does not guarantee support for every possible Kali utility.

### Command reference

| Command | Description |
|:--|:--|
| `/help` · `/tools` | Help and discovered MCP tools |
| `/inventory` | Installed-tool inventory |
| `/ad <target> [domain]` | Bounded Active Directory discovery |
| `/ldap <target> [baseDN]` | LDAP discovery and base-scope query |
| `/rag tools` | View indexed MCP tool catalog |
| `/rag build` | Build local technical index |
| `/rag search <query>` | Search technical knowledge |
| `/rag reload` | Reload documentation |
| `/toolhelp <binary>` | Retrieve local executable help |
| `/remember <note>` · `/memories` | Save / read notes |
| `/clear` · `/reset` · `/quit` | Clear screen / reset context / exit |

**Illustrative requests (not execution evidence):**

```text
H4X > /tools
H4X > /rag build
H4X > /rag search kerberos
H4X > scan localhost quickly with Nmap
H4X > analyze the returned results
```

### Scoped automatic scanning

Explicitly approved Nmap targets can be configured through `H4X_AUTO_TARGETS` **inside `hax.sh`**, before it launches Python:

```bash
export H4X_AUTO_TARGETS="localhost,127.0.0.1,::1,lab.example"
```

Names are matched exactly: `lab.example` is not the same entry as `www.lab.example`. Public deployments should default to loopback-only. This setting does not replace the requirement to obtain authorization.

### Known limitations

- Tool support depends on the connected MCP server schemas and installed executables.
- Model-generated commands and interpretations may be incorrect.
- Technical RAG currently uses lexical retrieval, not vector embeddings.
- A reconstructed command preview does not prove a command ran; inspect the actual tool result.
- The repository does not claim live, end-to-end verification against the reader's setup.

---

<a id="français"></a>
# 🇫🇷 Français

## Présentation

**H4X LLM Agent** connecte un modèle Ollama local à **Kali MCP Server** et **MetasploitMCP** pour proposer une interface conversationnelle de tests de sécurité dans le terminal. Il associe découverte des outils MCP, routage adapté à la demande, recherche documentaire technique et mémoire persistante.

H4X assiste un opérateur expérimenté : **il ne remplace ni son jugement ni une validation technique des résultats**.

### Fonctionnalités principales

| Module | Fonction |
|:--|:--|
| **IA locale** | Orchestration d'un modèle via Ollama |
| **Kali MCP** | Découverte et appel des outils exposés par le serveur MCP |
| **MetasploitMCP** | Intégration d'une instance Metasploit RPC configurée |
| **RAG technique** | Recherche dans les schémas MCP, aides locales et documentation |
| **Routage des outils** | Conversion des intentions explicites en paramètres, notamment Nmap |
| **Terminal interactif** | Affichage Rich, historique modifiable et aperçu des commandes |
| **Active Directory** | Reconnaissance AD, DNS, SMB et LDAP bornée |
| **Mémoire locale** | Conservation des notes de l'opérateur entre les sessions |
| **Contrôles** | Cibles autorisées explicites et confirmation des actions sensibles |

### Prérequis

- Kali Linux, de préférence dans une VM isolée
- Python 3 et `venv`
- Ollama avec un modèle compatible téléchargé localement
- Kali MCP Server et MetasploitMCP
- Metasploit Framework, RPC et PostgreSQL pour l'intégration Metasploit

> [!NOTE]
> Les noms des paquets et les commandes de démarrage MCP peuvent varier selon la version de Kali. Vérifie les exécutables effectivement présents. Le lanceur actuel utilise des privilèges élevés et doit rester réservé à un environnement dédié.

### Installation rapide

```bash
git clone https://github.com/St0rn/H4X-LLM-Agent.git
cd H4X-LLM-Agent

python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt

# Installer Ollama et configurer les deux serveurs MCP au préalable.
ollama pull qwen2.5:7b

chmod +x hax.sh
sudo bash ./hax.sh
```

**Examine `hax.sh` avant de l'exécuter en root.** Conserve les mots de passe RPC et autres secrets hors de Git.

### RAG technique

Le RAG repose sur un **index lexical** construit à partir des noms, descriptions et schémas JSON des outils MCP. Il peut également indexer les sorties `--help` des utilitaires installés ainsi que les documents textuels du projet. Il ne s'agit pas d'une base vectorielle et cela ne garantit pas la prise en charge de tous les utilitaires Kali.

### Commandes disponibles

| Commande | Description |
|:--|:--|
| `/help` · `/tools` | Aide et outils MCP découverts |
| `/inventory` | Inventaire des utilitaires installés |
| `/ad <cible> [domaine]` | Découverte Active Directory bornée |
| `/ldap <cible> [baseDN]` | Découverte LDAP et requête ciblée |
| `/rag tools` | Catalogue technique des outils MCP |
| `/rag build` | Construction de l'index local |
| `/rag search <requête>` | Recherche dans la documentation |
| `/rag reload` | Rechargement de la documentation |
| `/toolhelp <binaire>` | Aide locale d'un exécutable |
| `/remember <note>` · `/memories` | Enregistrement et consultation des notes |
| `/clear` · `/reset` · `/quit` | Effacement de l'écran / contexte / sortie |

**Exemples de saisie (sans prétendre à une exécution réelle) :**

```text
H4X > /tools
H4X > /rag build
H4X > /rag search kerberos
H4X > fais un scan Nmap rapide sur localhost
H4X > analyse les résultats obtenus
```

### Cibles Nmap autorisées

Pour les scans Nmap automatiques, renseigne les cibles **exactement autorisées** dans `hax.sh`, avant le lancement du Python :

```bash
export H4X_AUTO_TARGETS="localhost,127.0.0.1,::1,lab.example"
```

`lab.example` et `www.lab.example` sont deux entrées différentes. La configuration publique devrait autoriser uniquement le loopback par défaut. L'autorisation contractuelle demeure indispensable.

### Limites connues

- Les capacités réelles dépendent des schémas MCP et des outils installés.
- Le modèle peut se tromper dans une commande ou son interprétation.
- Le RAG utilise une recherche lexicale, sans embeddings vectoriels.
- Un aperçu de commande n'est pas une preuve d'exécution : vérifie la réponse réelle de l'outil.
- Aucune validation d'intégration complète sur toutes les installations Kali n'est revendiquée.

---

## Project structure / Structure du projet

```text
H4X-LLM-Agent/
├── agent.py           # Orchestration, MCP, terminal
├── hax.sh             # Startup launcher / Lanceur
├── ad_tools.py        # AD / LDAP helpers
├── technical_rag.py   # Local technical retrieval
├── requirements.txt   # Python dependencies / Dépendances
├── docs/              # Documentation
├── tests/             # Developer tests / Tests développeur
├── LICENSE            # MIT
└── README.md          # English + Français
```

## Security & contributions / Sécurité et contributions

- [Security policy / Politique de sécurité](SECURITY.md)
- [Contribution guide / Guide de contribution](CONTRIBUTING.md)
- [Changelog / Historique](CHANGELOG.md)
- [MIT License / Licence MIT](LICENSE)

<div align="center">

**Built by St0rn — [Cybersecur'IT](https://www.cybersecurit.fr)**

*For research, education and authorized security operations.*  
*Pour la recherche, la formation et les audits de sécurité autorisés.*

</div>
