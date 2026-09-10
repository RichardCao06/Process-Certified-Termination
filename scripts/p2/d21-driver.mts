/** PCT-P2-001 / D21: frozen DSH fixture driver with official user patches.
 * No controller hook is registered. Raw events travel only to the parent pipe.
 */
import type { Context } from '@deepseek-ai/cordis'
import type {} from '@deepseek-ai/dsh-tools'
import { boot, installFailLoud, loadOptionalPatches, resolveConfigPath } from '@deepseek-ai/dsh-app-boot'
import { runFixtureTurn } from '@deepseek-ai/dsh-loader-smoke'
import type { SessionEvent } from '@deepseek-ai/dsh-session'

const NAME = 'pct-p2-d21-driver'
const [baseConfig, patchFile, mode, task] = process.argv.slice(2)
if (!baseConfig || !patchFile || !['no-model', 'fixture'].includes(mode)
  || (mode === 'fixture' && !task)) throw new Error('Invalid D21 driver arguments')

const uninstall = installFailLoud(NAME)
let ctx: Context | undefined
try {
  const patches = loadOptionalPatches(NAME, patchFile)
  if (!patches?.length) throw new Error('Official patch list is empty')
  ctx = await boot(NAME, resolveConfigPath(baseConfig, undefined), patches)
  await ctx.loader.await()
  const tools = ctx.tools.schemas().map(tool => tool.name).sort()
  const entries = new Map([...ctx.loader.entries()].map(entry => [entry.options.id, entry]))
  const disabled = ['subprocess', 'bash', 'subagent', 'subagent-spawn-in-process',
    'subagent-fork-in-process', 'tool-subagent-control', 'tool-subagent-report',
    'tool-subagent', 'tool-subagent-fork', 'workflow-worker-thread', 'tool-workflow',
    'tool-ralph', 'tool-todo']
  const llm = entries.get('llm-deepseek')?.fiber?.config as any
  const spine = entries.get('agent-spine')?.fiber?.config as any
  const checks = {
    exact_tools: JSON.stringify(tools) === JSON.stringify(['edit', 'read', 'write']),
    capabilities_disabled: disabled.every(id => entries.get(id)?.disabled === true
      && entries.get(id)?.fiber === undefined),
    worker_profile: llm?.models?.length === 1 && llm.models[0].id === 'deepseek-v4-pro'
      && llm.thinking === 'enabled' && llm.reasoningEffort === 'high'
      && llm.maxTokens === 16000 && llm.defaultContextWindow === 128000
      && llm.retryPolicy?.maxRetries === 0,
    spine_boundary: spine?.tools?.mode === 'native' && spine.skills?.enabled === false
      && spine.toolBash === false && spine.toolJobs === false && spine.goals === false,
  }
  if (!Object.values(checks).every(Boolean)) throw new Error('D21 runtime boundary mismatch')
  process.stdout.write(`${JSON.stringify({ type: 'd21_boot', mode, checks, tools })}\n`)
  if (mode === 'fixture') {
    const result = await runFixtureTurn(ctx, {
      task,
      onEvent: (sessionId: string, event: SessionEvent) => {
        process.stdout.write(`${JSON.stringify({ type: 'session_event', sessionId, event })}\n`)
      },
    })
    process.stdout.write(`${JSON.stringify(result)}\n`)
  }
} catch (error: unknown) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exitCode = 1
} finally {
  await ctx?.fiber.dispose()
  uninstall()
}
