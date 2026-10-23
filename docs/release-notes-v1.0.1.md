# better-deepseek-harness-vanilla v1.0.1 发行说明

> **安装修复版**。基座、插件版本、挂载/屏蔽划分、50 个 skill 与 v1.0.0 **完全相同**，
> 只修了一处会让启动器装不上的 pnpm 配置。

## 问题：启动器安装报「安装整合包依赖失败」

报错栈（DSHL / dsh PCL 启动器）：

```
安装整合包依赖失败
  在 DSHL.ModPnpmOperations.RunPnpmImportSteps
→ 依赖安装失败（退出码 1）：
Error: ERR_PNPM_IGNORED_BUILDS
  ╰─▶ Ignored build scripts: @google/genai@2.21.0, protobufjs@7.6.6
首次锁文件安装（退出码 1）：
Error: ERR_PNPM_NO_LOCKFILE
```

容易误读的一点：**依赖其实已经装完了**（日志里 139 个包全部 `added`），失败发生在收尾的 build-script 审批检查上；
而第二条 `ERR_PNPM_NO_LOCKFILE` 是连带结果 —— 启动器的流程是「先跑一次普通安装生成 `pnpm-lock.yaml` → 再跑 frozen 安装」，
第一次非零退出就没写出锁文件，第二次自然报「没有锁文件」。**修好第一条，第二条自动消失。**

## 根因

pnpm 12 默认把「带 `install` / `prepare` 脚本、但没有被显式批准」的依赖当作**致命错误**（`strictDepBuilds` 默认开）。
本包的来源链条（用 `pnpm why` 定位）：

```
protobufjs@7.6.6
└─┬ @google/genai@2.21.0        （package.json 里有 "prepare": "node scripts/prepare.js"）
  └─┬ @earendil-works/pi-ai@1.3.0
    └─┬ dsh-workbuddy-connect@0.7.9
      └── better-deepseek-harness-vanilla (本包)
```

- `@google/genai`：`prepare` 是它自己仓库的构建脚本，发布产物已含 dist，**运行时不需要**；
- `protobufjs`：`postinstall` 只是自检/提示脚本，**运行时不需要**。

## 修法

`pnpm-workspace.yaml` 增加两段（带注释）：

```yaml
strictDepBuilds: false
ignoredBuiltDependencies:
  - '@google/genai'
  - 'protobufjs'
```

### 一个反直觉的实测结论（重要，写给以后的我）

在 pnpm **12.14.0** 上分别试了三种写法（每种的完整 20 依赖安装都实跑过）：

| 写法 | 结果 |
|---|---|
| `ignoredBuiltDependencies: [@google/genai, protobufjs]`（仅此） | ❌ 仍报 `ERR_PNPM_IGNORED_BUILDS` |
| `onlyBuiltDependencies: [@google/genai, protobufjs]`（仅此，等于「批准执行」） | ❌ 仍报同一个错 |
| **`strictDepBuilds: false`**（+ ignored 列表记录知情） | ✅ 安装成功 |

也就是说：pnpm 12 里 `pnpm approve-builds` 的产物不再是这两个键能替代的，
**唯一能把该错误降级为「跳过」的开关是 `strictDepBuilds`**。忽略列表仍保留，用于记录「我们明确知道且不需要这些脚本」。

## 端到端验证（本机实测）

1. **复现**：按本包 `package.json` 建临时工程，原配置跑 `pnpm install` → 稳定复现 `ERR_PNPM_IGNORED_BUILDS`；
2. **修复后全量安装**：23 个依赖（含 3 个 git 依赖 `dsh-computer-use` / `dsh-agent-arena` / `dsh-qqbot`）
   全新安装 **Done in 1m 7.5s**，退出码 0；
3. **模拟启动器第二步**：紧接着 `pnpm install --frozen-lockfile` → `Lockfile is up to date` + **Done in 61ms**；
4. **打包**：`python scripts/build-dspack.py . .` 成功，`manifest.version = 1.0.1`，50 个 skill 在位。

## 安装时仍会看到、但**不影响成功**的提示

```
[WARN] deprecated dsh-workbuddy-connect@0.7.9        # 上游已停止维护（我们在文档里标注过）
[WARN] Tarball download average speed … below 50 KiB/s   # 只是网速提示
[WARN] 1 deprecated subdependencies found: node-domexception@1.0.0
Agent skills awaiting approval: @liustack/modlens, dsh-computer-use@…     # pnpm 12 的新提示，非致命
[WARN] Issues with peer dependencies found            # 因为暂屏蔽插件的依赖仍在，属预期
```

实测这些全部出现时**退出码仍为 0**。

## 计数（与 v1.0.0 一致）

| 项 | 值 |
|---|---|
| 基座 | DSH 0.2.1-rc.2 |
| 挂载插件 | 10 个 |
| 暂屏蔽插件（仍随包安装） | 13 个 |
| `dependencies` / `bundles` | 23 / 12 |
| 自带 skill | 50 个 |
| compat-check | 挂载 10/10 通过 |

## 发行资产

`better-deepseek-harness-vanilla-1.0.1.dspack` 与同名 `.dspack.sha256`（64 字节十六进制，无换行）。
GitHub Release 为**正式发行**（未登记到 `docs/prerelease-versions.txt`）。
