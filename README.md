# 更好的 deepseek harness（原版风格）

[English](README.en.md) | 简体中文

面向 **Coding 用户**的 DeepSeek Harness 整合包 · **原版风格**。
基座 **DSH 0.2.1-rc.2**。

> 整合包标识 `better-deepseek-harness-vanilla`（仓库名 / `.dspack` 前缀 / profile 名）。
> 社区整合包，非 DeepSeek 官方产品。

## 这个包是什么

它是 [`better-deepseek-harness-codex`](https://github.com/yukitakasama/better-deepseek-harness-codex) 的同源变体：
**插件集与基座完全相同（对齐 codex 版 v3.0.0），唯一差别是不装 `@michengai/dsh-codex-ui`**。

- 因此**界面是 DSH 官方的样子** —— 官方侧栏、官方设置页、官方会话标题生成，一行都没被改造过。
- 换来的是更少的 UI 层接管：不会出现「侧栏被重建」「设置页被替换」这类副作用，出问题时排查范围也更小。
- 代价是少了 Codex 风格的工作区会话树、全局搜索、轮次跳转等界面增强（那些都来自 `dsh-codex-ui`）。

两个包**可以并存在同一台机器上**（profile 名不同、互相独立），想切风格就切 profile。

## 装什么（挂载 10 个插件）

| 能力 | 插件 | 版本 |
|---|---|---|
| `/review` 独立子 Agent 代码审查 | `@michengai/dsh-code-review` | 1.0.1 |
| `/simplify` 按 Git 变更范围简化代码 | `@michengai/dsh-simplify` | 1.0.1 |
| 只读旁问，不打断主任务 | `@michengai/dsh-btw` | 1.0.4 |
| 费用与余额计量、模型价格、Coding Plan 额度 | `dsh-cost-meter` | 1.9.30 |
| 桌宠：蓝色大肥鱼，97 段透明动画、可多开、可选桌面小窗 | `dsh-pet` | 0.3.8 |
| 上下文可视化仪表盘 | `dsh-context` | 0.74.0 |
| 每个子代理独立选模型 | `dsh-plugin-subagent-director` | 0.6.0-beta.2 |
| 多智能体团队协作 | `@nanmicoder/dsh-agent-teams` | 0.1.26 |
| Git 分支图 | `@linxin666/dsh-client-ui-git-graph` | 0.4.8 |
| WorkBuddy 桌面端模型接入（复用 App 登录态，未登录自动隐藏） | `dsh-workbuddy-connect` | 0.7.9 |

外加两个官方基座 bundle（`@deepseek-ai/dsh-base`、`@deepseek-ai/dsh-web-app`），bundles 共 12 行。

**落点说明**：没有 codex-ui 之后，`dsh-cost-meter` 的余额卡片进官方侧栏底部（`sidebar.footer.action`），
它与 `dsh-pet` 的设置分区进官方设置页（`settings.section`）—— 这些插槽由 DSH 官方提供，不需要本包做任何补丁。

## 暂屏蔽（随包安装、不挂载）的 13 个

判据与 codex 版完全一致：**上游没有明确声明适配 DSH 0.2.1-rc.2 的，一律不加载**（避免兼容门禁拒装或启动崩溃）。
它们仍在 `dependencies` 里（装着，随时可启用），只是不在 `dsh.profile.bundles`：

| 插件 | 钉版本 | 屏蔽原因 |
|---|---|---|
| `dsh-ops` | 0.3.0 | 仅 `^0.2.0-rc.2` 范围覆盖，未点名 rc.2 |
| `@goodandready/dsh-context-lens` | 0.1.28 | 仅 `^0.1.7-rc.2 \|\| ^0.2.0-rc.1` 范围覆盖 |
| `@goodandready/dsh-key-limits` | 0.2.19 | 无任何 `@deepseek-ai/dsh-*` peer → 无法确认 |
| `dsh-plugin-wallpaper-engine` | 1.2.0 | 仅 `>=0.2.0-rc.1` 范围覆盖 |
| `@modusensus/dsh-mneme` | 0.8.13 | 仅开区间覆盖；新版另带 `dsh-better-sidebar` peer |
| `@mrweicodes/dsh-loop-guard` | 1.0.8 | 仅开区间覆盖 |
| `dsh-computer-use-win` | 0.2.3 | 无 `@deepseek-ai/dsh-*` peer → 无法确认 |
| `dsh-computer-use` | fork `72f390a` | peer 全为 `*`，无 compat 声明，上游停更于 2026-09-15 |
| `dsh-prompt` | 0.3.0 | 仅 `engines.dsh >=0.2.0-rc.2` 范围覆盖 |
| `@liustack/modlens` | 3.26.6 | 无任何 peer / engines 声明 → 无法确认 |
| `dsh-effort-slider` | 1.3.1 | 无任何兼容声明，上游 2026-09-26 后停更 |
| `dsh-agent-arena` | fork `25e2c55` | 上游精确钉 `0.2.0-rc.2` → 未适配 |
| `@tencent-connect/dsh-qqbot` | fork `7e88006` | 仅 `>=0.1.0-rc.6` 范围覆盖 |

**启用步骤**：把包名加回 `package.json` → `dsh.profile.bundles`，删掉 `overrides/cordis.patch.yml` 里对应的 `disabled: true`，
一次只开一个再验证。

## 安装

需要 **DSH 0.2.1-rc.2**（`dshVersion` 精确锁定该版本）。

```bash
dsh --profile better-deepseek-harness-vanilla
```

或由 DSH 启动器导入 `better-deepseek-harness-vanilla-<version>.dspack`。

> **git 依赖**：本包仍有 3 个 git 依赖（`dsh-computer-use`、`dsh-agent-arena`、`@tencent-connect/dsh-qqbot`），
> 安装时需要能访问 GitHub。它们都已暂屏蔽（不挂载）但仍留在 `dependencies` 里；若网络拉不动，
> 可以把它们从 `package.json` 删掉，挂载集不受影响。

> **WorkBuddy 前提**：`dsh-workbuddy-connect` 复用 WorkBuddy 桌面 App 的**本机登录态**，所以要先安装并登录
> WorkBuddy（国内版或国际版均可）才会出现对应模型分组；**没装也不影响启动**，分组直接隐藏。
> 注意该插件上游已在 npm 标记 **停止维护**（deprecated），仍可用但今后不再更新。

## 自带的 50 个 skill

安装时 `home/skills/` 会落入 `DSH_HOME/skills/`，开箱即用：设计/前端、动效、数据分析、代码开发、办公文档、
浏览器自动化（含 ego-lite 的 `ego-browser`）等。

`ego-browser` 来自 [citrolabs/ego-lite](https://github.com/citrolabs/ego-lite) v2.1.0，以 **skill** 形态投递
（上游的 DSH 插件入口 `@citrolabs/ego` 在 git 安装时因软链的 Skill 目录被 npm/pnpm 打包丢弃而在 import 阶段
`ENOENT`，其官方 npm 包也未发布；skill 载荷与那个插件注册的内容完全相同）。

**第一次用之前要装 ego lite 本体**：macOS 可用 skill 自带的 `scripts/install.sh`；**Windows 没有安装脚本**，
需到 <https://lite.ego.app/> 下载安装包，完成 onboarding 后 `ego-browser` 才会写进 PATH（只有之后新开的终端才认识）。

## 兼容性判定

DSH 用 `semver.satisfies(宿主版本, peer范围, { includePrerelease: true })` 校验；本包宿主版本 = `0.2.1-rc.2`。
「明确声明适配」= `dsh.compatibility.dshReleases` 写了 rc.2、或 peer 精确枚举 rc.2、或 `engines.dsh` 点名 `>=0.2.1-rc.x`。

```bash
node docs/compat-check.cjs   # 已挂载 10/10 通过；暂屏蔽 13 个单列
```

> 提醒：精确枚举型 peer（MichengAI 三件套、agent-teams、workbuddy）写死的是已知 RC 白名单，宿主升到
> `0.2.1-rc.3` 会被整行禁用，必须等上游重发。

## 自定义

- **换插件版本**：改 `package.json` 的 `dependencies`/`bundles` 与 `manifest.json` 的镜像字段（两处必须一致）。
- **本包 patch 层**（`overrides/cordis.patch.yml`）默认几乎为空：只保留 `dsh-computer-use-win` 的 MCP 路径修正与
  暂屏蔽条目的 `disabled: true`。**不要在这里去 disable 官方的 `ui-sidebar` / `ui-settings-general`** ——
  那等于把这个包变成半个 codex 版，且会破坏官方插槽的落点。
- **从头改样式**：想要 Codex 风格请直接用 [codex 版](https://github.com/yukitakasama/better-deepseek-harness-codex)。

## 许可与致谢

本整合包仅为插件组合与配置，不含插件源码（`home/skills/` 下的 skill 文本版权归各作者，`ego-browser` 归 citrolabs，MIT）。

- [MichengAI](https://github.com/MichengAI)（Code Review / Simplify / BTW）
- [PC2005-cloud](https://github.com/PC2005-cloud/dsh-pet)（桌宠 dsh-pet）
- [corrinehu](https://github.com/corrinehu/dsh-workbuddy-connect)（WorkBuddy 模型接入）
- [citrolabs](https://github.com/citrolabs/ego-lite)（ego-lite / `ego-browser` skill）
- `dsh-cost-meter`、`dsh-context`、`@modusensus/dsh-mneme`、`@liustack/modlens`、`dsh-prompt`、`dsh-ops`、
  `dsh-client-ui-git-graph`、`@nanmicoder/dsh-agent-teams`、`dsh-plugin-subagent-director`、`@mrweicodes/dsh-loop-guard`、
  `@goodandready/*`、`dsh-plugin-wallpaper-engine`、`dsh-effort-slider`、`dsh-computer-use-win` 等各作者
- fork 依赖 `dsh-agent-arena`、`dsh-qqbot` 由本仓库维护分叉，功能版权归上游原作者

格式规范：[DSH-PackForge](https://github.com/DSH-PackForge/DSH-PackForge)。

## 更新日志

### v1.0.0 (2026-10-23)（正式发行）

- **首个版本**。内容 = `better-deepseek-harness-codex` **v3.0.0** 去掉 `@michengai/dsh-codex-ui`（1.1.47）：
  - 依赖 24 → **23**，bundles 26 → **12**（10 个插件 + 2 个官方基座）；
  - 其余 10 个挂载插件版本、13 个暂屏蔽插件、13 条暂屏蔽原因**全部与 codex 版 v3.0.0 相同**；
  - 50 个自带 skill 相同（含 ego-lite `ego-browser`）；
  - 基座同为 **DSH 0.2.1-rc.2**，`dshVersions` 只声明该版本。
- **UI 差异**：官方侧栏 / 官方设置页 / 官方会话标题全部保留；`dsh-cost-meter` 与 `dsh-pet` 的设置分区落在官方
  `settings.section`，余额卡片落在官方 `sidebar.footer.action`。
- **patch 层**：因不再有 codex-ui 接管，本包 `overrides/cordis.patch.yml` 里与 codex-ui 相关的说明全部改写；
  实际生效的补丁只剩 `dsh-computer-use-win` 的 MCP 路径修正 + 5 条暂屏蔽 `disabled: true`。
- **验证**：`node docs/compat-check.cjs` → 已挂载 **10/10 通过** peer 门禁、exit 0；
  `package.json` / `manifest.json` 的 deps（23）与 bundles（12）集合一致；`scripts/build-dspack.py` 打包成功。
- **未验证**：未在真实 DSH 0.2.1-rc.2 宿主上跑 `--dump-config` / 启动冒烟（与 codex 版同一限制）。
