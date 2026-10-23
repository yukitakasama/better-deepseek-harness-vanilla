# better-deepseek-harness-vanilla v1.0.0 发行说明（**预发布 pre-release**）

> **原版风格**整合包：与 `better-deepseek-harness-codex` v3.0.0 同基座、同插件集，
> **唯一差别是不装 `@michengai/dsh-codex-ui`** —— 界面完全走 DSH 官方实现。

## 这个包存在的理由

`dsh-codex-ui` 做的是一件霸道但有价值的活：它 disable 掉官方 `ui-sidebar` / `ui-settings-general` / `session-title-llm`，
然后自己重建 Codex 风格的侧栏与设置页。好处是界面更顺手；代价是：

- 所有依赖 `sidebar.footer.action` / `settings.section` 的下游插件，落点变成「codex-ui 重新提供的插槽」而不是官方插槽，
  一旦 codex-ui 出问题（或与宿主新版本的 UI 冲突），整条 UI 链都会跟着受影响；
- 排查界面问题时，无法用「官方行为」做基线对照。

本包把这一层拿掉，给你一个**可对照的原版基线**：同一套插件、同一个基座，只换 UI 归属。

## 与 codex 版的逐项对照

| 项 | codex v3.0.0 | vanilla v1.0.0 |
|---|---|---|
| 基座 | DSH 0.2.1-rc.2 | **相同** |
| 挂载插件 | 11 个 | **10 个**（去掉 `@michengai/dsh-codex-ui` 1.1.47） |
| 暂屏蔽插件 | 13 个（版本与原因完全一致） | **相同** |
| `dependencies` 条数 | 24 | **23** |
| `bundles` 行数 | 13（11 + 2 基座） | **12**（10 + 2 基座） |
| 自带 skill | 50 个 | **50 个（相同）** |
| UI | Codex 风格侧栏 / 设置页 | **DSH 官方侧栏 / 设置页** |
| patch 层生效内容 | MCP 路径修正 + 5 条屏蔽 | **相同**（与 codex-ui 相关的说明已改写） |

### 挂载清单（10 个）

| 插件 | 版本 | 作用 |
|---|---|---|
| `@michengai/dsh-code-review` | 1.0.1 | `/review` 独立子 Agent 代码审查 |
| `@michengai/dsh-simplify` | 1.0.1 | `/simplify` Git 范围代码简化 |
| `@michengai/dsh-btw` | 1.0.4 | 只读旁问 |
| `dsh-cost-meter` | 1.9.30 | 费用 / 余额 / 模型价格 / Coding Plan 额度 |
| `dsh-pet` | 0.3.8 | 桌宠（蓝色大肥鱼，97 段透明动画，可多开，可选桌面小窗） |
| `dsh-context` | 0.74.0 | 上下文可视化仪表盘 |
| `dsh-plugin-subagent-director` | 0.6.0-beta.2 | 子代理独立选模型（上游 latest 即 beta） |
| `@nanmicoder/dsh-agent-teams` | 0.1.26 | 多智能体团队协作 |
| `@linxin666/dsh-client-ui-git-graph` | 0.4.8 | Git 分支图 |
| `dsh-workbuddy-connect` | 0.7.9 | WorkBuddy 桌面端模型接入（上游已 deprecated） |

### 暂屏蔽清单（13 个，与 codex 版一致）

`dsh-ops` 0.3.0、`@goodandready/dsh-context-lens` 0.1.28、`@goodandready/dsh-key-limits` 0.2.19、
`dsh-plugin-wallpaper-engine` 1.2.0、`@modusensus/dsh-mneme` 0.8.13、`@mrweicodes/dsh-loop-guard` 1.0.8、
`dsh-computer-use-win` 0.2.3、`dsh-computer-use`（git `72f390a`）、`dsh-prompt` 0.3.0、`@liustack/modlens` 3.26.6、
`dsh-effort-slider` 1.3.1、`dsh-agent-arena`（git `25e2c55`）、`@tencent-connect/dsh-qqbot`（git `7e88006`）。

判据、原因与「如何重新启用」见 README 的「暂屏蔽」表格与 codex 版 `docs/release-notes-v3.0.0.md`。

## UI 落点变化（本包的核心差异）

| 元素 | codex 版 | vanilla 版 |
|---|---|---|
| 侧栏 | `dsh-codex-ui` 重建（官方 `ui-sidebar` 被 disable） | **官方 `ui-sidebar`** |
| 设置页 | `dsh-codex-ui` 重建（官方 `ui-settings-general` 被 disable） | **官方 `ui-settings-general`** |
| 会话标题 | `dsh-codex-ui` 关掉 `session-title-llm` | **官方 `session-title-llm` 生效** |
| 余额/费用卡片 | codex-ui re-provide 的 `sidebar.footer.action` | **官方 `sidebar.footer.action`** |
| cost-meter / dsh-pet 设置 | codex-ui re-provide 的 `settings.section` | **官方 `settings.section`** |

也就是说：下游插件的落点插槽名完全一样，只是「由谁提供」从 codex-ui 换回官方。**因此这两个插件的设置项不会有功能缺失**，
但视觉位置会跟着官方布局走（不再在 Codex 风格设置页里）。

## 仓库与命名

- 仓库：`yukitakasama/better-deepseek-harness-vanilla`
- 包标识 / profile 名：`better-deepseek-harness-vanilla`（与 codex 版只差后缀，`dspack` 前缀按包名生成）
- 显示名：中文「更好的 deepseek harness（原版风格）」/ 英文「Better DeepSeek Harness (Vanilla Style)」
- 两个包可并存：profile 名不同，互不覆盖

## 验证与未验证项

已验证：

- `node --check docs/compat-check.cjs` 通过；`node docs/compat-check.cjs` **已挂载 10/10 通过** peer 门禁、exit 0，
  暂屏蔽 13 个单列（其中 6 个无任何 `@deepseek-ai/dsh*` peer 声明）；
- `package.json` / `manifest.json` 的 `dependencies`（23）与 `bundles`（12）集合逐一比对一致；README 中英表行一致；
- `overrides/cordis.patch.yml` YAML 解析通过，结构为 5 条 `disabled: true` 屏蔽 + `im-qqbot` 默认关 + `pwsh-sandbox` 平台守卫；
- `python scripts/build-dspack.py . .` 打包成功，包内 `manifest.version = 1.0.0`、`dshVersion = 0.2.1-rc.2`、50 个 skill。

**未验证**：与 codex 版同一限制 —— 没有在真实 DSH 0.2.1-rc.2 宿主上跑 `--dump-config` 或启动冒烟，
也没有做 UI 回归（特别是「去掉 codex-ui 后官方侧栏 + cost-meter 余额卡 + dsh-pet 设置分区」这三处落点）。
装好后建议先确认：官方侧栏正常、余额卡片在位、设置页里能看到 cost-meter 与 dsh-pet 两个分区、桌宠照常出现。

## 发行资产

`better-deepseek-harness-vanilla-1.0.0.dspack` 与同名 `.dspack.sha256`（64 字节十六进制，无换行）。
GitHub Release 标记为 **Pre-release**；`docs/prerelease-versions.txt` 已登记 `1.0.0`。
