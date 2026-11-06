# Changelog

## 0.1.1 — MCP error handling (2026-11-06)

- Recognize application-level MCP errors reported as `status: error`.
- Prevent the same failed tool call from being executed repeatedly within one LLM turn.
- Block a Metasploit tool call if its selected module contradicts an explicit x64 architecture request.
- Add regression tests for these cases.
- This is a client-side robustness fix; the underlying Metasploit RPC response issue is not yet fixed.


## 0.1.0 — Initial public source package (2026-11-06)

- Ollama conversational CLI with Kali MCP and MetasploitMCP support.
- Local documentation retrieval and MCP tool schema catalogue.
- Local persistent notes and keyboard command history.
- Nmap command preview and bounded AD/LDAP discovery helpers.
- Colored terminal output, Rich Markdown rendering and bilingual documentation.

This is an initial source publication, **not a fully validated release**. Integration against live Kali/Ollama/Metasploit services has not been independently verified.
