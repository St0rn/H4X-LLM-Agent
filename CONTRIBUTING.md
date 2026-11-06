# Contributing / Contribuer

## English

1. Open an issue describing the problem, expected behavior and a sanitized reproduction.
2. Fork and create a focused branch (`fix/...` or `feat/...`).
3. Add tests for parsing, argument validation and MCP routing; avoid tests that target public networks.
4. Run `python3 -m compileall -q agent.py ad_tools.py technical_rag.py`, `bash -n hax.sh` and `python3 -m unittest discover -s tests`.
5. Submit a pull request in English or French. No secrets, real customer outputs or private IP ranges linked to customers.

## Français

1. Ouvre une issue avec le problème, le comportement attendu et une reproduction anonymisée.
2. Crée une branche dédiée et limite la portée des changements.
3. Ajoute des tests sans trafic sur des réseaux publics.
4. Vérifie la compilation Python, la syntaxe Bash et les tests.
5. Propose une pull request en français ou en anglais, sans secrets ni résultats clients.
