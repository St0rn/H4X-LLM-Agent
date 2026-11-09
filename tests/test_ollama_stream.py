"""Tests unitaires du streaming Ollama sans serveur externe."""
from h4x_ollama_stream import _visible, _merge_calls


def test_hide_thinking_blocks():
    assert _visible("<think>secret</think>\n# Visible") == "\n# Visible"
    assert _visible("<think>secret incomplet") == ""
    assert _visible("réponse") == "réponse"


def test_incremental_tool_calls():
    indexed, anonymous = {}, []
    _merge_calls(indexed, anonymous, [
        {"index": 0, "function": {"name": "kali__nmap_scan",
                                  "arguments": '{"target":"'}}])
    _merge_calls(indexed, anonymous, [
        {"index": 0, "function": {"name": "kali__nmap_scan",
                                  "arguments": '127.0.0.1"}'}}])
    assert indexed[0]["function"]["arguments"] == '{"target":"127.0.0.1"}'
    assert indexed[0]["function"]["name"] == "kali__nmap_scan"


def test_unindexed_no_duplicate():
    indexed, anonymous = {}, []
    call = {"function": {"name": "get_status", "arguments": {}}}
    _merge_calls(indexed, anonymous, [call])
    _merge_calls(indexed, anonymous, [call])
    assert len(anonymous) == 1
