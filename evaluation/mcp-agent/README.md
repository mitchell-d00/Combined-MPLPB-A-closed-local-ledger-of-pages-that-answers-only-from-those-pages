# Local MCP agent integration evidence

Last reviewed: 2026-11-08.

Baseline: `acf7800a5f8320ec29ee957d002eaaba8ed4e816`. `baseline.json` retains the
preimplementation checks and observations. `acceptance.frozen.json` and its
checksum froze 16 model-authored acceptance scenarios before implementation.
They are authored development/acceptance data, not independent human validation.

The adapter delegates to the full native `App`; the reader and original source
fixtures are unchanged. `tests/test_mcp_agent.py` covers protocol recovery,
malformed/oversized messages, exact source parity, unrelated material, source
changes/withdrawal, contradictions, heading-only evidence, profile/scope/path
boundaries, user-context authority, source instructions, capture integrity,
procedure clarification/reconnect and transactional conversation-size rejection.
`tools/check_mcp_client.py` uses the separately installed official MCP Python SDK
to exercise actual stdio processes and a conversation resumed after a restart.

Retained `focused-tests.json` and `sdk-client.json` record actual execution;
`validation.json` records revisions/content identity and known release limits
when those checks complete. New output belongs in a new file, not over the
frozen acceptance questions or earlier reports.

```sh
python -m unittest tests.test_mcp_agent -v
python -m venv /tmp/mplpb-client-check
/tmp/mplpb-client-check/bin/python -m pip install 'mcp==1.26.0'
/tmp/mplpb-client-check/bin/python tools/check_mcp_client.py --output NEW_MCP_REPORT.json
```

Protocol success does not prove an external AI faithfully relays the result.
There is no new independent model accuracy, human usability, shared-service
security or deployed-site claim from these checks. See
[enforced rules](../../docs/MCP_AGENT.md) and
[readiness limits](../../docs/PRODUCTION_READINESS.md).
