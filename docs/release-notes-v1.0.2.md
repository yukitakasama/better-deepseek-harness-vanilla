# better-deepseek-harness-vanilla v1.0.2 发行说明

> **预发布（pre-release）· 工作区 / 目录选择器修复**。
> 基座、10 个挂载插件版本、其余 12 个暂屏蔽插件、50 个 skill 与 v1.0.1 **完全相同**，
> 只删掉一个「装着不加载、却在偷偷改写模块解析」的依赖。

## 症状

在 DSH **0.2.1-rc.2** 宿主上装 v1.0.1，点侧栏 **选择工作区 → 添加工作区**，前端直接弹错：

```
directory picker failed: typert gateway: directoryPicker/pick:
  active Service "directoryPickerController" is unavailable
```

同一台机器上 codex 版（宿主 0.2.0-rc.2）点同一个按钮完全正常。

## 根因链（每一环都实测过）

1. **profile 的 `node_modules` 里混进了核心包。** 暂屏蔽列表里的 `dsh-prompt@0.3.0` 虽然不在
   `dsh.profile.bundles` 里，但它在 `dependencies` 里，于是 pnpm 照样装它；而它
   **硬依赖**（不是 peer）`@deepseek-ai/dsh-storage-domain@^0.2.0-rc.2`。
   预发布版本号在 semver 里的规则是「`^0.2.0-rc.2` 不包含 0.2.1-rc.x」，所以 pnpm 只能落 0.2.0-rc.2，
   于是 `<profile>/node_modules/@deepseek-ai/dsh-storage-domain` 出现了 **0.2.0-rc.2 的副本**。

2. **DSH 解析 bundle 是「profile 优先」。** `dsh-app-boot` 的注释写得很明确：

   > Module resolution is two-anchor by construction: a bundle name resolves … profile directory.
   > **Pnpm-managed entries in the profile's `node_modules` resolve first.** The runtime resolution
   > supplies packages carried by the installation …

   所以核心 `dsh-base` 里的 `storage-domain` 行，实际加载的是 **profile 里那份 0.2.0-rc.2**，
   而不是宿主自带的 0.2.1-rc.2。

3. **兼容门禁把整行禁用。** 启动期 preflight 读到 0.2.0-rc.2 的清单，判定它与宿主 0.2.1-rc.2 不兼容：

   ```
   dsh: disabling profile plugin row "storage-domain": Plugin @deepseek-ai/dsh-storage-domain@0.2.0-rc.2
   is incompatible with dsh 0.2.1-rc.2: requirements {"@deepseek-ai/dsh-invariants":"0.2.0-rc.2",
   "@deepseek-ai/dsh-storage":"0.2.0-rc.2"}. … Exact-version exemption: not active.
   ```

4. **级联 pending。** 没有 `storageDomain` 服务之后：

   ```
   dsh: warning: 7 entries did not activate
   session-projection-cache : pending (waiting for service: storageDomain)
   workspace                : pending (waiting for service: storageDomain)
   session-controller       : pending (waiting for service: workspaceRegistry)
   schedule                 : pending (waiting for services: storageDomain, sessionController)
   workspace-controller     : pending (waiting for service: workspaceRegistry)
   ui-deliverables          : pending (waiting for service: sessionController)
   ui-git-graph             : pending (waiting for service: workspaceRegistry)
   ```

5. **`directoryPickerController` 就在这一行里。** `@deepseek-ai/dsh-api-workspace-controller`
   这一个包里既有 `WorkspaceController`（inject `remoteAccess/typert/workspaceRegistry`），
   也有 `DirectoryPickerController`（`Remote('pick')` → 命名空间 `directoryPicker`）。
   整行 pending = 两个服务都没实例化；而 Typert 网关的 Remote 描述符是静态注册的（所以能解析
   `directoryPicker/pick` 这个端点），但取不到活动实例，于是回你
   `active Service "directoryPickerController" is unavailable`。

## 为什么当前 codex 实例不会出现

codex 版 v2.8.1 跑在 **宿主 0.2.0-rc.2** 上：profile 里那份 `dsh-storage-domain@0.2.0-rc.2` 与宿主版本**完全一致**，
兼容门禁无话可说，一行都不禁用 —— 同样的隐藏状态，只是不发作。
换句话说：**这不是 codex/vanilla 的差别，是宿主版本与 profile 里那份核心包版本的差别**；
codex 版一旦升到 0.2.1-rc.2 基座，会以一模一样的方式坏掉。

## 修法

1. **把 `dsh-prompt` 从 `dependencies` 移除**（它本来就没挂载，装着唯一的后果是污染解析锚点）。
   `pnpm-workspace.yaml` 里它的 `minimumReleaseAgeExclude` 条目一并删掉。
   暂屏蔽数 13 → **12**，`dependencies` 23 → **22**。
2. **加防回归门（打包期）**：`scripts/build-dspack.py` 新增依赖审计 ——
   逐个依赖查 `npm view <pkg>@<ver> dependencies`，只要某个依赖声明了 `@deepseek-ai/dsh-*` **硬依赖**
   （这类包理应走 `peerDependencies`），构建直接失败并打印修法。
   以后再加插件，不会静默把这个坑重新带进包里。
   网络不可用时会降级为警告（可用 `--no-dep-audit` / `DSH_PACK_SKIP_DEP_AUDIT=1` 显式跳过）。

> 为什么不选「给 `@deepseek-ai/dsh-storage-domain` 加 pnpm override 钉回 0.2.1-rc.2」：
> 那样 profile 里会多出一份**与宿主同版本**的核心包副本，副作用只是被压住而不是消失
> （两个模块实例、两份 cordis 服务定义的风险仍在）。一个本来就该走 peer 的依赖，不该由分发方来兜。

## 端到端验证（本机实测）

用一个临时 profile 做 A/B 启动对比（`package.json` / `cordis.patch.yml` 复制自本包，
`node_modules` 每个条目 junction 到本机已安装的 profile，只单独控制「遮蔽副本在不在」）：

| 变体 | 启动日志 |
|---|---|
| **保留** `node_modules/@deepseek-ai/dsh-storage-domain` | `disabling profile plugin row "storage-domain"`；`warning: 6 entries did not activate`（缺 `storage-domain` → `workspace` → `workspace-controller` 全 pending） |
| **移除**该目录（= v1.0.2 的形态） | 无兼容门禁告警；**pending 归零**；`storage-domain` / `workspace` / `workspace-controller` 全部激活 → `directoryPickerController` 有实例 |

另外：`node docs/compat-check.cjs` → 已挂载 **10/10 通过**；`python scripts/build-dspack.py . .` → 打包 + 新依赖审计通过。

## 计数（相对 v1.0.1 的变化）

| 项 | v1.0.1 | v1.0.2 |
|---|---|---|
| 基座 | DSH 0.2.1-rc.2 | DSH 0.2.1-rc.2 |
| 挂载插件 | 10 | 10 |
| 暂屏蔽插件（仍随包安装） | 13 | **12**（`dsh-prompt` 不再安装） |
| `dependencies` / `bundles` | 23 / 12 | **22** / 12 |
| 自带 skill | 50 | 50 |

## 已装 v1.0.1 的临时自救办法

不想等新版的话，两步即可（任选其一）：

```powershell
# ① 直接删掉 profile 里那份被遮蔽的核心包，重启实例
Remove-Item -Recurse -Force "<profiles>\better-deepseek-harness-vanilla\node_modules\@deepseek-ai\dsh-storage-domain"

# ② 或从 package.json 的 dependencies 里删掉 "dsh-prompt"，重新 pnpm install
```

重启后启动日志里不应再出现 `disabling profile plugin row "storage-domain"`。

## 发行资产

`better-deepseek-harness-vanilla-1.0.2.dspack` 与同名 `.dspack.sha256`（64 字节十六进制，无换行）。
GitHub Release 登记在 `docs/prerelease-versions.txt` → **预发布（pre-release）**。
