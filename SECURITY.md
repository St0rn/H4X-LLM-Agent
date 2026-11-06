# Security / Sécurité

## English

H4X is designed for **authorized security assessments and isolated labs**. The launcher is configured to run as root; this gives tools powerful host permissions. Do not run against systems outside your written scope. MCP tools may execute commands and could be exposed to prompt injection in untrusted output. Verify arguments, preserve audit logs securely and use a disposable Kali VM or snapshot.

**Never commit:** `.msf-rpc-secret`, `data/`, `logs/`, `.env`, credential caches, captured tickets, reports containing client data or proprietary documents. The `.gitignore` covers common cases but is not a substitute for reviewing `git status` and `git diff --cached`.

The public package defaults automatic Nmap targets to loopback. To add an authorized target, edit `H4X_AUTO_TARGETS` in `hax.sh` or configure the variable in the launch context; `sudo` may strip environment variables. Sensitive operations are subject to interactive approval in the shipped code. No guarantee of security or correctness is made.

To report a security issue, contact the maintainer privately via the contact information at https://www.cybersecurit.fr rather than publishing live exploit details in a public issue.

## Français

H4X s'utilise exclusivement pour des **audits autorisés et des laboratoires isolés**. Le lanceur utilise root et donne des droits élevés aux outils. Les sorties MCP peuvent contenir des prompt injections ; vérifie les paramètres, protège les journaux et utilise une VM jetable.

**Ne publie jamais** `.msf-rpc-secret`, `data/`, `logs/`, des caches Kerberos, identifiants, captures, rapports ou documents clients. Le `.gitignore` réduit les risques mais ne remplace pas une revue des fichiers préparés pour le commit.

Les cibles Nmap automatiques par défaut sont limitées au loopback. Ajoute uniquement des cibles dont tu as l'autorisation. Les actions sensibles continuent de demander une validation interactive dans cette version. Aucun fonctionnement ni sécurité ne sont garantis.
