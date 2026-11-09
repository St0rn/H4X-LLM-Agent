"""Streaming Ollama pour H4X : Markdown Rich, thinking caché, outils MCP préservés."""
import json
import re
import time

from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text


def _visible(text):
    """Ne montre jamais les blocs de raisonnement explicites du modèle."""
    text = re.sub(r'<think\b[^>]*>.*?</think\s*>', '', text, flags=re.I | re.S)
    text = re.sub(r'<think\b[^>]*>.*$', '', text, flags=re.I | re.S)
    text = re.sub(r'</think\s*>', '', text, flags=re.I)
    return text


def _combine_fragment(old, new):
    if not isinstance(new, str) or not new:
        return old
    if not isinstance(old, str) or not old:
        return new
    if new == old or new.startswith(old):
        return new
    if old.endswith(new):
        return old
    return old + new


def _merge_calls(indexed, anonymous, tool_calls):
    """Reconstruit les appels indexés, évite les doublons non indexés complets."""
    for call in tool_calls or []:
        if not isinstance(call, dict):
            continue
        func = call.get('function')
        if not isinstance(func, dict):
            continue
        idx = call.get('index')
        if not isinstance(idx, int):
            if call not in anonymous:
                anonymous.append(call)
            continue
        dest = indexed.setdefault(idx, {'type': 'function', 'function': {'name': '', 'arguments': ''}})
        out = dest['function']
        out['name'] = _combine_fragment(out.get('name', ''), func.get('name', ''))
        args = func.get('arguments')
        if isinstance(args, dict):
            previous = out.get('arguments')
            out['arguments'] = {**(previous if isinstance(previous, dict) else {}), **args}
        elif isinstance(args, str):
            out['arguments'] = _combine_fragment(out.get('arguments', ''), args)


def _render(text, fmt):
    if fmt == 'plain':
        return Text(text)
    return Markdown(text, code_theme='monokai')


async def stream_chat(client, url, payload, console, fmt='auto'):
    """Flux /api/chat sans exposer le raisonnement et en préservant les outils MCP."""
    request = {**payload, 'stream': True}
    if 'qwen3.5' in str(request.get('model', '')).lower():
        request['think'] = False

    content = []
    indexed, anonymous = {}, []
    last = {}
    last_rendered = ''
    last_paint = 0.0
    with Live(Text('[cyan]H4X // Génération...[/cyan]'), console=console,
              refresh_per_second=7, transient=True, vertical_overflow='visible') as live:
        async with client.stream('POST', url, json=request) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get('error'):
                    raise RuntimeError('Ollama: ' + str(data['error']))
                msg = data.get('message') or {}
                if not isinstance(msg, dict):
                    continue
                piece = msg.get('content')
                if isinstance(piece, str) and piece:
                    content.append(piece)
                # message.thinking est volontairement ignoré.
                _merge_calls(indexed, anonymous, msg.get('tool_calls'))
                visible = _visible(''.join(content))
                now = time.monotonic()
                if visible != last_rendered and (now - last_paint > 0.12 or data.get('done')):
                    live.update(_render(visible, fmt))
                    last_rendered, last_paint = visible, now
                if data.get('done'):
                    last = data
            visible = _visible(''.join(content))
            if visible and visible != last_rendered:
                live.update(_render(visible, fmt))

    calls = [indexed[k] for k in sorted(indexed)] + anonymous
    result_message = {'role': 'assistant', 'content': _visible(''.join(content))}
    if calls:
        result_message['tool_calls'] = calls
    if last.get('done_reason') == 'length':
        console.print('[yellow][!] Génération interrompue à la limite num_predict.[/yellow]')
    return {'message': result_message, 'done_reason': last.get('done_reason'),
            'eval_count': last.get('eval_count')}
