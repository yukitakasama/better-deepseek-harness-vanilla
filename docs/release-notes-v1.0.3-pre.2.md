# better-deepseek-harness-vanilla v1.0.3-pre.2 发行说明

> **预发布（pre-release）· 修复「启动器安装整合包失败（exit code 0xc0000409）」**。
> 基座仍是 DSH **0.2.1-rc.2**；挂载的 11 个插件、暂屏蔽的 11 个插件、50 个 skill
> 与 v1.0.3-pre.1 **完全相同**。

## 这次改了什么

- **dsh-ops 的 fork 产物改为随包内置**：`vendor/dsh-ops-0.4.1-dsh021.1.tgz`
  （sha512 固定在 `scripts/build-dspack.py`），打包时展开到 dspack 的
  `overrides/dsh-ops/`。
- `package.json` / `manifest.json` 里 `dsh-ops` 的依赖从 GitHub Releases 的 tgz URL
  改为 `link:./dsh-ops`。
- **`@dsh-ops/bash-win32-x64@0.2.1` 提升为显式依赖**（npm registry，安装时自动拉取）：
  `link:` 不会安装被链接包自身的 `optionalDependencies`，不补这一行 Windows 上
  `ops_bash` 会静默缺失（`resolveShells` 报 `declared but not installed`）。
- 安装期不再访问 `github.com`；`dsh-ops` 相关下载只走 `registry.npmjs.org`。

## 问题现象

v1.0.3-pre.1 在启动器里导入会停在这一步：

```
$ <launcher>	ools\pnpm.cmd install --no-frozen-lockfile --store-dir ... 
error: pnpm install（整合包） 失败: $ ... pnpm.cmd install --no-frozen-lockfile ...
```

启动器日志里只有退出码：

```
[WARN] pnpm install（整合包） 失败（exit code: 0xc0000409）: $ ... pnpm.cmd install ...
```

`0xc0000409`（STATUS_STACK_BUFFER_OVERRUN）在这里不是 pnpm 的业务错误，而是进程直接
异常终止；pnpm 的 stdout/stderr 一行都没来得及输出，所以启动器只能回显命令行本身。

## 根因

- pre.1 把 `dsh-ops` 写成了
  `https://github.com/yukitakasama/dsh-ops/releases/download/v0.4.1-dsh021.1/dsh-ops-0.4.1-dsh021.1.tgz`。
- pnpm 对 **URL 依赖**没有 registry 元数据可查，每次安装都必须真实下载该 URL。
- 本机到 `github.com` / `objects.githubusercontent.com` /
  `release-assets.githubusercontent.com` 的 TLS 被代理拦截，Node 内置 CA 不信任代理
  根证书，握手报 `UNABLE_TO_VERIFY_LEAF_SIGNATURE`；pnpm 在「下载直接依赖」阶段异常
  退出，于是只留下 `0xc0000409`。
- 实测同一网络下 `registry.npmjs.org`、`codeload.github.com` 可达，因此不是「整台机器
  没网」，而是「GitHub 的 release 资产域名不可直连」。
- 手动加 `NODE_OPTIONS=--use-system-ca` 后，pre.1 能完整装完 134 个包；但整合包无法
  控制启动器传给 pnpm 的 Node 参数，所以只能在包这一侧消除该 URL 依赖。

## 修复方式

1. 把 fork 的 release tgz（6.9 MB，`sha512 7oEJvHf...XQ==`）放进 `vendor/`，作为不可变
   输入提交进仓库。
2. `scripts/build-dspack.py` 新增 `collect_vendor_entries()`：打包前校验 tgz 的 sha512，
   缺失或被替换会**直接拒绝打包**；校验通过则去掉归档里的 `package/` 前缀，把整棵树写进
   dspack 的 `overrides/dsh-ops/**`。
3. launcher 的导入顺序是「先 `pnpm install`，再把 `overrides/` 覆盖到 profile 根」
   （`modpack.rs::apply_overrides`），所以 `overrides/dsh-ops/` 最终落点是
   `<profile>/dsh-ops/`。
4. profile 的 `package.json` 写 `"dsh-ops": "link:./dsh-ops"`。安装时 target 还不存在，
   pnpm 只创建一个指向它的 junction 并打印一条 WARN（不是错误）；`overrides/` 落地后
   junction 立即生效，DSH 解析 bundle 时能读到完整的 `package.json` 与 `lib/`。
5. 依赖表补上 `@dsh-ops/bash-win32-x64: 0.2.1`。原因：`link:` 的语义是「只建链接、不装
   被链接包的依赖」，而 Windows 的 `ops_bash` 需要这个载荷（`os: ["win32"]`，
   装上约 307 MB）。在 Linux/macOS 上 pnpm 仍会装一份该包（不影响使用，可手动删掉这一行）。

## 验证

- 最小工程 `{"dsh-ops":"link:./dsh-ops"}` + 包的 `pnpm-workspace.yaml`：pnpm 11.28.6
  安装成功（只有一条 non-existent directory 警告）。
- 把 fork 包树放到 `<profile>/dsh-ops/` 后，`node_modules\dsh-ops` junction 能解析到
  `dsh-ops@0.4.1-dsh021.1`，`lib/index.js` 存在。
- 用启动器同款 pnpm 11.28.6 按「manifest 生成 package.json → install → 覆盖 overrides」
  的完整顺序跑通：`exit 0`，`node_modules/@dsh-ops/bash-win32-x64/bin/bash.exe` 存在，
  `resolveShells()` 返回 `bash: available: true (source: bundled)`。
- 重新打出的 dspack 解包后含 `overrides/dsh-ops/package.json`、
  `overrides/dsh-ops/lib/index.js` 与三平台 `runtime/`。
- 不改变 dsh-ops 的任何代码、peer 范围或 `overrides/cordis.patch.yml` 的启用行。

## 已知限制 / 回退

- dspack 体积增加约 7 MB（fork 的三平台 Rust worker 原样保留，未裁剪）。
- Windows 首次安装会额外下载 `@dsh-ops/bash-win32-x64`（约 307 MB 解开后体积）；
  这是 dsh-ops 用来提供 `ops_bash` 的钉版 bash（PortableGit），不是本包自己加的。
- 仓库多一个 6.9 MB 的 `vendor/dsh-ops-0.4.1-dsh021.1.tgz`；升级 fork 时需同时更新
  tgz 与 `scripts/build-dspack.py` 里的 `DSH_OPS_SHA512`。
- 回退到 pre.1 的行为：把 `dsh-ops` 依赖改回 URL、删掉 `vendor/` 与打包脚本里的 vendor
  分支即可（不推荐，会重新引入本 bug）。
