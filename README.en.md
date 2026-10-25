# Better DeepSeek Harness (Vanilla Style)

简体中文 | English

A DeepSeek Harness modpack for **Coding users** · **vanilla style**.
Built on **DSH 0.2.1-rc.2**.

> Modpack identifier: `better-deepseek-harness-vanilla` (repo name / `.dspack` prefix / profile name).
> Community modpack — not an official DeepSeek product.

## What this pack is

It is a sibling of [`better-deepseek-harness-codex`](https://github.com/yukitakasama/better-deepseek-harness-codex):
**same plugin set and same host (aligned with codex v3.0.0), with exactly one difference — it does not install `@michengai/dsh-codex-ui`.**

- So the UI is **DSH's own**: official sidebar, official settings page, official session-title generation — nothing is taken over.
- In exchange you get fewer UI-level takeovers to reason about: no rebuilt sidebar, no replaced settings page.
- The trade-off is losing the Codex-style workspace session tree, global search and turn navigation (all of which come from `dsh-codex-ui`).

Both packs **can be installed side by side** (different profile names, fully independent) — switch styles by switching profiles.

## What's inside (11 mounted plugins)

| Capability | Plugin | Version |
|---|---|---|
| `/review` independent code review | `@michengai/dsh-code-review` | 1.0.1 |
| `/simplify` Git-scoped simplification | `@michengai/dsh-simplify` | 1.0.1 |
| Read-only side-ask without interrupting the main task | `@michengai/dsh-btw` | 1.0.4 |
| Cost & balance metering, model prices, coding-plan quota | `dsh-cost-meter` | 1.9.30 |
| Desk pet: blue big fish, 97 transparent animations, multiple pets, optional desktop window | `dsh-pet` | 0.3.8 |
| Context dashboard | `dsh-context` | 0.74.0 |
| Per-subagent model selection | `dsh-plugin-subagent-director` | 0.6.0-beta.2 |
| Multi-agent teams | `@nanmicoder/dsh-agent-teams` | 0.1.26 |
| Git branch graph | `@linxin666/dsh-client-ui-git-graph` | 0.4.8 |
| WorkBuddy desktop model access (reuses the app sign-in; hides when signed out) | `dsh-workbuddy-connect` | 0.7.9 |
| Native file / Bash tooling (`ops_*`, temporary local fork, payload bundled in-pack) | `dsh-ops` | 0.4.1-dsh021.1 |

Plus the two official base bundles (`@deepseek-ai/dsh-base`, `@deepseek-ai/dsh-web-app`) — 13 bundles in total.

**Where things land**: without codex-ui, `dsh-cost-meter`'s balance card renders into the official `sidebar.footer.action`,
and its settings plus `dsh-pet`'s settings render into the official `settings.section`. Those slots are provided by DSH itself,
so this pack needs no patch for them.

## Shelved (installed, not mounted): 11 plugins

The criterion is identical to the codex edition: **if upstream has not explicitly declared 0.2.1-rc.2 support, it is not loaded**
(to avoid a peer-gate rejection or a startup crash). They stay in `dependencies` (installed, re-enableable) but are not in `dsh.profile.bundles`:

| Plugin | Pinned | Why shelved |
|---|---|---|
| `@goodandready/dsh-context-lens` | 0.1.28 | Range coverage only (`^0.1.7-rc.2 \|\| ^0.2.0-rc.1`) |
| `@goodandready/dsh-key-limits` | 0.2.19 | No `@deepseek-ai/dsh-*` peer at all → cannot confirm |
| `dsh-plugin-wallpaper-engine` | 1.2.0 | Range coverage only (`>=0.2.0-rc.1`) |
| `@modusensus/dsh-mneme` | 0.8.13 | Open-range coverage only; newer versions add a `dsh-better-sidebar` peer |
| `@mrweicodes/dsh-loop-guard` | 1.0.8 | Open-range coverage only |
| `dsh-computer-use-win` | 0.2.3 | No `@deepseek-ai/dsh-*` peer at all → cannot confirm |
| `dsh-computer-use` | fork `72f390a` | Peers are all `*`, no compat statement; upstream stopped 2026-09-15 |
| `@liustack/modlens` | 3.26.6 | No peer / engines declaration at all → cannot confirm |
| `dsh-effort-slider` | 1.3.1 | No compat statement at all; upstream stopped 2026-09-26 |
| `dsh-agent-arena` | fork `25e2c55` | Upstream pins `0.2.0-rc.2` exactly → not adapted |
| `@tencent-connect/dsh-qqbot` | fork `7e88006` | Range coverage only (`>=0.1.0-rc.6`) |

**Note (v1.0.2 onward)**: `dsh-prompt@0.3.0` is now **removed from `dependencies` entirely** (no longer installed at all).
It was not merely "range coverage": it hard-depends on the core package `@deepseek-ai/dsh-storage-domain@^0.2.0-rc.2`, which pnpm
installs into the profile's `node_modules`, shadowing the host's own 0.2.1-rc.2 copy, tripping the compatibility gate into
disabling the `storage-domain` row and taking the workspace API and the directory picker down with it
(see the [v1.0.2 release notes](docs/release-notes-v1.0.2.md)). To re-enable it, upstream first has to turn that dependency
into a peerDependency.

**To re-enable**: add the package back to `package.json` → `dsh.profile.bundles`, delete the matching `disabled: true` in
`overrides/cordis.patch.yml`, and enable one at a time.

## Installation

Requires **DSH 0.2.1-rc.2** (`dshVersion` pins exactly that version).

```bash
dsh --profile better-deepseek-harness-vanilla
```

Or import `better-deepseek-harness-vanilla-<version>.dspack` from the DSH launcher.

> **Bundled dsh-ops**: the dsh-ops fork payload ships inside the pack
> (`vendor/dsh-ops-0.4.1-dsh021.1.tgz`, expanded into the dspack's `overrides/dsh-ops/`, with the
> dependency written as `link:./dsh-ops`), so installation **does not need GitHub**.
> The Windows bash payload `@dsh-ops/bash-win32-x64@0.2.1` is now an explicit dependency (fetched from
> the npm registry): `link:` does not install the linked package's optionalDependencies, so without it
> `ops_bash` would silently go missing.
> See the [v1.0.3-pre.2 release notes](docs/release-notes-v1.0.3-pre.2.md).

> **Git dependencies**: the pack still carries 3 (`dsh-computer-use`, `dsh-agent-arena`, `@tencent-connect/dsh-qqbot`),
> so installation requires access to GitHub. All three are shelved (not mounted) but remain in `dependencies`; if your
> network cannot fetch them, delete them from `package.json` — the mounted set is unaffected.

> **WorkBuddy prerequisite**: `dsh-workbuddy-connect` reuses the WorkBuddy desktop app's **local sign-in**, so the model
> groups only appear after WorkBuddy (domestic or international) is installed and signed in. **Not installing it breaks
> nothing** — the group simply hides. Note upstream has marked the package **deprecated** on npm; it works but will not be updated.

## Install troubleshooting

**Symptom**: the launcher reports "failed to install modpack dependencies", ending with
`Error: ERR_PNPM_IGNORED_BUILDS / Ignored build scripts: @google/genai@2.21.0, protobufjs@7.6.6`,
followed by a second failure `first lockfile install → ERR_PNPM_NO_LOCKFILE` (a knock-on effect of the first).

**Cause**: pnpm 12 treats dependencies with `install`/`prepare` scripts that have not been approved as a **fatal error**.
The chain here is `dsh-workbuddy-connect@0.7.9` → `@earendil-works/pi-ai@1.3.0` →
`@google/genai@2.21.0` (`prepare`) → `protobufjs@7.6.6` (`postinstall`).

**Fixed in v1.0.1**: `pnpm-workspace.yaml` now sets `strictDepBuilds: false` plus an `ignoredBuiltDependencies` list.
Note that in pnpm 12 `onlyBuiltDependencies` / `ignoredBuiltDependencies` **on their own do not** clear the error (measured);
only `strictDepBuilds` downgrades it from fatal to skipped.

**These are harmless notices** (measured exit code 0): `Agent skills awaiting approval: @liustack/modlens, dsh-computer-use@…`,
`deprecated dsh-workbuddy-connect@0.7.9`, `Issues with peer dependencies found`.

## The 50 bundled skills

On install, `home/skills/` lands in `DSH_HOME/skills/`: design/frontend, motion, data analysis, coding, office documents,
browser automation (including ego-lite's `ego-browser`) and more.

`ego-browser` comes from [citrolabs/ego-lite](https://github.com/citrolabs/ego-lite) v2.1.0 and ships as a **skill**
(upstream's DSH plugin entry `@citrolabs/ego` breaks when installed from git — npm/pnpm drop its symlinked Skill directory,
so it throws `ENOENT` at import — and its official npm package was never published; the skill payload is exactly what that
plugin registers).

**Install ego lite itself first**: macOS can use the skill's `scripts/install.sh`; **Windows has no install script** — download
the installer from <https://lite.ego.app/>, finish onboarding, and only terminals opened afterwards will see `ego-browser`.

**Symptom**: the launcher log only shows `pnpm install（整合包） failed (exit code: 0xc0000409)` and pnpm printed nothing.

**Cause**: v1.0.3-pre.1 pinned `dsh-ops` to a GitHub Releases tgz URL, so every install had to reach
`github.com`; when TLS is intercepted by a proxy Node cannot verify the certificate, the process aborts,
and the launcher can only record the exit code.

**Fixed in v1.0.3-pre.2**: the fork payload is vendored in-pack and the dependency is `link:./dsh-ops`,
so installation never touches GitHub. Make sure you are installing **pre.2 or newer**.


## Compatibility criteria

DSH validates with `semver.satisfies(hostVersion, peerRange, { includePrerelease: true })`; this pack's host is `0.2.1-rc.2`.
"Explicitly declared" means: `dsh.compatibility.dshReleases` names rc.2, or the peer range enumerates rc.2, or `engines.dsh`
names `>=0.2.1-rc.x`.

```bash
node docs/compat-check.cjs   # mounted 11/11 pass; 11 shelved reported separately
```

> `dsh-ops` is the only exception: upstream 0.4.1 only declares `^0.2.0-rc.2`, so this release temporarily mounts
> the local fork `0.4.1-dsh021.1` (peer adds `^0.2.1-rc.2`, Rust worker unchanged with the upstream three-platform
> payloads), verified with the 0.2.1-rc.2 host packages via typecheck / build / 127 suites. Since v1.0.3-pre.2 the
> payload ships inside the pack (`link:./dsh-ops`), so installation does not touch GitHub. Switch back to the
> official package once upstream names rc.2.

> Note: enumeration-style peers (the three MichengAI plugins, agent-teams, workbuddy) hard-code a whitelist of known RCs, so a
> host bump to `0.2.1-rc.3` disables those rows until upstream republishes.

## Customization

- **Change plugin versions**: edit `package.json` (`dependencies` / `bundles`) and the mirrored fields in `manifest.json` — they must match.
- **The patch layer** (`overrides/cordis.patch.yml`) is deliberately near-empty here: only the `dsh-computer-use-win` MCP path fix
  and the `disabled: true` shelving entries. **Do not disable the official `ui-sidebar` / `ui-settings-general` rows there** —
  that would turn this into half a codex edition and break the official slots the other plugins rely on.
- **Want the Codex style?** Use the [codex edition](https://github.com/yukitakasama/better-deepseek-harness-codex) instead.

## License & acknowledgements

This modpack is only a plugin combination and configuration; it does not contain plugin source code (the Skill text under
`home/skills/` belongs to the respective authors; `ego-browser` is citrolabs, MIT).

- [MichengAI](https://github.com/MichengAI) (Code Review / Simplify / BTW)
- [PC2005-cloud](https://github.com/PC2005-cloud/dsh-pet) (desk pet dsh-pet)
- [corrinehu](https://github.com/corrinehu/dsh-workbuddy-connect) (WorkBuddy model access)
- [citrolabs](https://github.com/citrolabs/ego-lite) (ego-lite / the `ego-browser` skill)
- The respective authors of `dsh-cost-meter`, `dsh-context`, `@modusensus/dsh-mneme`, `@liustack/modlens`,
  `dsh-ops`, `dsh-client-ui-git-graph`, `@nanmicoder/dsh-agent-teams`, `dsh-plugin-subagent-director`, `@mrweicodes/dsh-loop-guard`,
  `@goodandready/*`, `dsh-plugin-wallpaper-engine`, `dsh-effort-slider`, `dsh-computer-use-win`
- The `dsh-agent-arena` and `dsh-qqbot` git dependencies are forks maintained in this repository; feature copyright remains with upstream

Format specification: [DSH-PackForge](https://github.com/DSH-PackForge/DSH-PackForge).

## Changelog

### v1.0.2 (2026-10-24) (pre-release · workspace / directory picker fix)

- **Fixes `typert gateway: directoryPicker/pick: active Service "directoryPickerController" is unavailable`** when adding a
  workspace on DSH 0.2.1-rc.2. In v1.0.1 the shelved `dsh-prompt@0.3.0` hard-depends on
  `@deepseek-ai/dsh-storage-domain@^0.2.0-rc.2`, so pnpm installed that copy into the profile's `node_modules`. DSH resolves
  bundle names profile-first with the installation as fallback, so the host's own 0.2.1-rc.2 copy was shadowed by 0.2.0-rc.2,
  the compatibility gate disabled the whole `storage-domain` row, and the `workspace` / `workspace-controller` chain
  (7 entries) stayed pending — taking the workspace API and the directory picker down with it.
- **Fix**: drop `dsh-prompt` from `dependencies` (it was never mounted, so all it did was poison the resolution anchor);
  shelved count 13 → **12**, `dependencies` 23 → **22**, and its `minimumReleaseAgeExclude` row removed from
  `pnpm-workspace.yaml`.
- **Regression guard**: `scripts/build-dspack.py` now audits dependencies at pack time — any dependency declaring a
  `@deepseek-ai/dsh-*` hard dependency (it should be a peerDependency) fails the build instead of shipping.
- **End-to-end verified**: A/B boot comparison on a throwaway profile (every `node_modules` entry junctioned to the installed
  one). With the shadow present: `disabling profile plugin row "storage-domain"` plus `6–7 entries did not activate`;
  without it: no gate warnings, zero pending entries, `storage-domain` / `workspace` / `workspace-controller` all active.
- **No other content changes**: host, the 10 mounted plugin versions, the remaining 12 shelved plugins and the 50 skills are
  identical to v1.0.1.

### v1.0.1 (2026-10-23) (stable release · install fix)

- **Fixed the launcher install failure** (`ERR_PNPM_IGNORED_BUILDS`): pnpm 12 makes unapproved dependency build scripts fatal,
  and this pack hits it through `dsh-workbuddy-connect` → `@earendil-works/pi-ai` → `@google/genai` (prepare) /
  `protobufjs` (postinstall). `pnpm-workspace.yaml` now sets `strictDepBuilds: false` and
  `ignoredBuiltDependencies: [@google/genai, protobufjs]`.
- **Also fixes** the follow-up `ERR_PNPM_NO_LOCKFILE`: the lockfile is only written once the first step succeeds, which the
  frozen install then reads.
- **Measured**: a clean install of all 23 dependencies (including 3 git ones) succeeds in **1m07s**, and the subsequent
  `pnpm install --frozen-lockfile` passes — matching the launcher's two-step flow.
- **No content changes**: host, plugin versions, mounted/shelved split and the 50 skills are identical to v1.0.0; only the
  install configuration was fixed.

### v1.0.0 (2026-10-23) (stable release)

- **First release.** Content = `better-deepseek-harness-codex` **v3.0.0** minus `@michengai/dsh-codex-ui` (1.1.47):
  - dependencies 24 → **23**, bundles 26 → **12** (10 plugins + 2 official bases);
  - the other 10 mounted plugin versions, the 13 shelved plugins and their 13 reasons are **identical** to codex v3.0.0;
  - the same 50 bundled skills (including ego-lite `ego-browser`);
  - same host **DSH 0.2.1-rc.2**, with `dshVersions` declaring only that version.
- **UI differences**: official sidebar / settings page / session titles are fully retained; `dsh-cost-meter` and `dsh-pet` settings
  land in the official `settings.section`, and the balance card in the official `sidebar.footer.action`.
- **Patch layer**: since no codex-ui takes anything over, every codex-ui-related note in `overrides/cordis.patch.yml` was rewritten;
  what actually takes effect is the `dsh-computer-use-win` MCP path fix plus 5 shelving `disabled: true` entries.
- **Verification**: `node docs/compat-check.cjs` → mounted **10/10 pass** the peer gate, exit 0; `package.json` / `manifest.json`
  deps (23) and bundles (12) sets match; `scripts/build-dspack.py` builds successfully.
- **Not verified**: no `--dump-config` / startup smoke test on a real DSH 0.2.1-rc.2 host (same limitation as the codex edition).
