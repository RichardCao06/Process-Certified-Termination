# DeepSeek Harness Event Mapping — P1 Development Note

## Baseline

- Repository: `deepseek-ai/deepseek-harness`
- Commit: `141eb6fef83422698aef7a981029e843e8161534`
- Status: selected P1 development baseline, not confirmatory freeze

The upstream lifecycle document distinguishes durable replay facts on `session/event` from live control/status on `agent/*`. At a natural stop with no pending next-step input, the loop invokes `agent/turn-stopping` before `turn/end`.

## Prototype mapping

| Upstream fact | PCT canonical class | Notes |
|---|---|---|
| `turn/start` | `TURN_START` | durable boundary |
| `turn/end` | `TURN_END` | preserve structured stop/error reason |
| `step/start` | `STEP_START` | durable boundary |
| `step/end` | `STEP_END` | durable boundary |
| `user/message` | `HUMAN_INPUT` or system-origin input | source kind must remain visible |
| `assistant/message` | `MODEL_MESSAGE` | not automatically a decision checkpoint |
| `tool/call` | `TOOL_CALL` | preserve call ID, name, and visible arguments under data policy |
| `tool/result` | `TOOL_RESULT` | durable result; authority is task-specific, not assumed by the mapper |
| `goal/change` | `GOAL_CHANGE` | goal revision and lifecycle change |
| `agent/inbox/*` | `INBOX_EVENT` | live coordination; useful for accepted/claimed/discarded work |
| `agent/error` | `ERROR` | distinguish method, provider, and infrastructure failures later |
| `tools/result` | live evidence candidate | immutable final tool outcome; correlate with durable `tool/result` |
| `agent/turn-stopping` | `CANDIDATE_STOP` | the primary PCT stop boundary |

## Important non-equivalences

- `assistant/message` is not proof of completion.
- a successful tool result is not automatically sufficient evidence for every obligation;
- `turn/end` is not equivalent to `CERTIFIED`;
- live `tools/result` and durable `tool/result` must be correlated without double-counting;
- a `max-tokens`, aborted, error, blocked, or budget ending must remain distinct from success.

## P1 implementation

`pct/dsh_mapping.py` provides a dependency-free prototype for mapping selected durable events and the turn-stopping checkpoint. It intentionally:

- does not install Hooks;
- does not steer the Worker;
- does not declare tool outcomes authoritative by default;
- does not expose hidden labels;
- does not certify completion.

A production adapter belongs to a later Work Order after the P1 annotation Gate.
