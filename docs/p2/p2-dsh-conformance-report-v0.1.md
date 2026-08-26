# P2 DeepSeek Harness Source/Envelope Conformance v0.1

**Frozen upstream:** `deepseek-ai/deepseek-harness@b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` (`dsh@0.1.1-rc.2`)

Authoritative CI independently checks the exact upstream commit and selected Git Blob SHAs, then verifies the frozen event vocabulary, `agent/turn-stopping` placement and native payload, ToolResultMessage structure, and PCT adapter normalization against a synthetic public envelope.

The conformance test uses no Worker model call and no natural task. A tool-reported `PASS` remains `authoritative=false` in the PCT event. Native `agent/turn-stopping` does not contain the complete PCT stop metadata; D12 resolves that gap with the explicit read-only sidecar.
