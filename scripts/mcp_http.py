"""MCP 서버를 HTTP로 직접 부르는 도우미. 단독으로 실행하지 않는다.

서버 주소와 헤더는 .mcp.json에서 읽고, 값 안의 ${VAR}는 환경 변수로 채운다.
call_tool(server, tool, arguments)는 initialize, notifications/initialized, tools/call 순서로 부르고
도구 결과(JSON 텍스트)를 (원문 텍스트, 읽은 값)으로 돌려준다.
요청 헤더와 토큰은 어떤 오류 메시지에도 넣지 않는다.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

from pipeline_io import ROOT

RETRY_WAITS = (2, 4, 8)
PROTOCOL = "2025-06-18"


class MCPError(RuntimeError):
    pass


def _expand(value, server):
    def sub(m):
        v = os.environ.get(m.group(1))
        if v is None:
            raise MCPError(f"{server}: 환경 변수 {m.group(1)}가 없습니다. 설정한 뒤 터미널을 다시 열어 주세요.")
        return v
    return re.sub(r"\$\{(\w+)\}", sub, value)


def server_config(server):
    path = ROOT / ".mcp.json"
    if not path.exists():
        raise MCPError(".mcp.json이 없습니다.")
    conf = json.loads(path.read_text(encoding="utf-8-sig")).get("mcpServers", {}).get(server)
    if not conf or not conf.get("url"):
        raise MCPError(f".mcp.json에 {server} 서버의 url이 없습니다.")
    headers = {k: _expand(str(v), server) for k, v in (conf.get("headers") or {}).items()}
    return _expand(conf["url"], server), headers


class Session:
    """서버 하나와의 MCP 세션. 처음 부를 때 initialize한다."""

    def __init__(self, server):
        self.server = server
        self.url, self.headers = server_config(server)
        self.session_id = None
        self.next_id = 0
        self.ready = False

    def _post_once(self, payload):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   **self.headers}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=headers,
                                     method="POST")
        with urllib.request.urlopen(req, timeout=600) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            body = resp.read().decode("utf-8")
            ctype = resp.headers.get("Content-Type", "")
        if not body.strip():
            return None
        if "text/event-stream" in ctype:
            msgs = [json.loads(line[5:].strip()) for line in body.splitlines()
                    if line.startswith("data:") and line[5:].strip()]
            for m in msgs:
                if m.get("id") == payload.get("id"):
                    return m
            return msgs[-1] if msgs else None
        return json.loads(body)

    def _post(self, payload):
        """네트워크 오류는 2초, 4초, 8초 쉬고 다시 부른다. HTTP 4xx는 바로 멈춘다."""
        what = payload.get("method")
        for attempt in range(len(RETRY_WAITS) + 1):
            try:
                return self._post_once(payload)
            except urllib.error.HTTPError as e:
                if e.code < 500 or attempt == len(RETRY_WAITS):
                    hint = " 토큰이 맞는지 확인해 주세요." if e.code in (401, 403) else ""
                    raise MCPError(f"{self.server} {what}: HTTP {e.code}.{hint}") from None
                err = f"HTTP {e.code}"
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt == len(RETRY_WAITS):
                    raise MCPError(f"{self.server} {what}: 네트워크 오류 {type(e).__name__}") from None
                err = type(e).__name__
            wait = RETRY_WAITS[attempt]
            print(f"  {self.server} {what}: {err}, {wait}초 뒤 다시 부릅니다.", flush=True)
            time.sleep(wait)

    def _rpc(self, method, params):
        self.next_id += 1
        r = self._post({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params})
        if r is None:
            raise MCPError(f"{self.server} {method}: 빈 응답")
        if "error" in r:
            raise MCPError(f"{self.server} {method}: {r['error'].get('message', r['error'])}")
        return r["result"]

    def start(self):
        if self.ready:
            return
        self._rpc("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                 "clientInfo": {"name": "review-pipeline", "version": "1"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.ready = True

    def call(self, tool, arguments):
        self.start()
        res = self._rpc("tools/call", {"name": tool, "arguments": arguments})
        text = "".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        if res.get("isError"):
            raise MCPError(f"{self.server} {tool}: 도구 오류 {text[:300]}")
        try:
            return text, json.loads(text)
        except json.JSONDecodeError:
            raise MCPError(f"{self.server} {tool}: 결과가 JSON이 아닙니다: {text[:200]}") from None


_SESSIONS = {}


def call_tool(server, tool, arguments):
    """도구 하나를 부르고 (원문 텍스트, 읽은 값)을 돌려준다. 같은 서버는 세션을 다시 쓴다."""
    if server not in _SESSIONS:
        _SESSIONS[server] = Session(server)
    return _SESSIONS[server].call(tool, arguments)
