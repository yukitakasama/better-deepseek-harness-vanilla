# better-deepseek-harness-vanilla v1.0.3-pre.1 发行说明

> **预发布（pre-release）· 启用 dsh-ops（本地 fork 临时适配 0.2.1-rc.2）**。
> 基座仍是 DSH **0.2.1-rc.2**；其余 10 个挂载插件、11 个暂屏蔽插件、50 个 skill 与 v1.0.2 **完全相同**。

## 这次改了什么

- **挂载 10 → 11**：新增 `dsh-ops`（原生 `ops_*` 文件 / Bash 工具集），并解除
  `overrides/cordis.patch.yml` 里 `dsh-ops-file` / `dsh-ops-shell` 两行的 `disabled`。
- **插件来源换成你的本地 fork**：
  `https://github.com/yukitakasama/dsh-ops/releases/download/v0.4.1-dsh021.1/dsh-ops-0.4.1-dsh021.1.tgz`
  （版本号 `0.4.1-dsh021.1`，GitHub Release 标记为 pre-release）。
- `pnpm-workspace.yaml` 里 `dsh-ops@0.3.0` 的 `minimumReleaseAgeExclude` 条目已移除（URL 依赖不受该闸门影响）。

## 为什么必须 fork

上游 `dsh-ops@0.4.1` 的 peer 只有 `@deepseek-ai/dsh: ^0.2.0-rc.2`。按 npm 的预发布语义，
`^0.2.0-rc.2` **不包含** `0.2.1-rc.2`（元组不同，需要 `includePrerelease` 才成立），
所以 DSH 启动期的兼容门禁会把整行禁用 —— 这就是 v1.0.0–v1.0.2 一直把它放在「暂屏蔽」的原因。

`0.2.1-rc.2` 相对 `0.2.0-rc.2` 还有两处真实 API 变化，光改 peer 范围不足以通过编译：

| 位置 | 0.2.1-rc.2 的变化 | fork 里的处理 |
|---|---|---|
| `@deepseek-ai/dsh-tools` | `ToolPresentationMode` 收窄为 `native \| ptc`，不再有 `both` | 目录里表示「两种呈现都可见」的 `both` 改为插件本地类型 `PresentationMode`，不再借用宿主联合类型 |
| `@deepseek-ai/dsh-client-ui-settings` | `ConfigFormSnapshot` 删除 `mode` 字段 | 设置页就绪判定改为 `status === 'ready' && writable`；若旧宿主仍带 `mode: 'host'` 也继续认 |

适配细节与验证过程见 fork 仓库 `docs/compat-dsh-0.2.1-rc.2.md`。

## 验证

在 Windows x64 + 宿主 `0.2.1-rc.2`（fork 的 devDependencies 全部指向 0.2.1-rc.2 宿主包）：

- `npm run typecheck`、`npm run build`、`npm run validate:manifest`、`npm run check:size` 全部通过。
- `node test/run.mjs`：127 套里 **125 套通过**、4 套按平台跳过、2 套失败（`bash-ipc` 私有 MSYS 运行时、
  `permissions` ACL fixture）；这 2 套在**未改动的上游 0.4.1 + 宿主 0.2.0-rc.2** 上同样失败，属于本机环境问题。
- 打包产物沿用上游三个平台（win32-x64 / linux-x64 / darwin-arm64）的 Rust worker 与 provenance 回执，
  只替换了 `lib/` 与 `package.json`、`dsh-plugin.json`。

## 已知限制 / 回退方式

- 这是**临时方案**：上游 `T-Auto/dsh-ops` 若发布点名适配 `0.2.1-rc.2` 的版本，应把
  `dependencies` 换回 `dsh-ops@<官方版本>`。
- 回退：把 `dsh-ops` 从 `package.json` / `manifest.json` 的 `dsh.profile.bundles` 移除，
  再在 `overrides/cordis.patch.yml` 给 `dsh-ops-file` / `dsh-ops-shell` 加回 `disabled: true`。
- 依赖 URL 下载需要能访问 GitHub（与本包已有的 `github:` 依赖前置条件相同）。
