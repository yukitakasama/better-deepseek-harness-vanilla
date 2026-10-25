#!/usr/bin/env python3
"""Build a DSH ``.dspack`` (format v3) zip plus its SHA-256 sidecar.

This mirrors the output that the ``dsh-packforge-app`` launcher produces for
the ``better-deepseek-harness-codex`` profile, so that the bundle can be
installed by ``dsh`` exactly like a launcher-built package.

Produced artifacts (named ``<manifest.name>-<manifest.version>.<ext>``):

* ``.dspack``  — a ZIP (DEFLATED) containing these entries, in order:
    - ``dspack.json``             (synthetic, 41 bytes, fixed content)
    - ``manifest.json``
    - ``package.json``
    - ``pnpm-workspace.yaml``
    - ``overrides/cordis.patch.yml``
    - ``overrides/dsh-ops/**``   (vendored from ``vendor/dsh-ops-*.tgz``;
                                   the launcher copies ``overrides/`` onto the
                                   profile root, so this lands at
                                   ``<profile>/dsh-ops/`` where the profile's
                                   ``"dsh-ops": "link:./dsh-ops"`` points)
    - ``home/skills/<name>/...``  (zero or more; each bundled skill ships
                                   under ``home/skills/`` so the launcher's
                                   import step copies it onto the DSH_HOME
                                   root → ``<DSH_HOME>/skills/<name>``)
* ``.dspack.sha256`` — lowercase hex SHA-256 of the ``.dspack`` file,
  64 bytes, **no** trailing newline.

Usage:
    python scripts/build-dspack.py [REPO_ROOT] [OUT_DIR]

Defaults: REPO_ROOT = repo root (parent of this script's dir),
OUT_DIR   = current working directory.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

# Exact bytes produced by dsh-packforge-app (41 bytes incl. trailing newline).
DSPACK_JSON = b'{\n  "format": "dspack",\n  "version": 3\n}\n'

# (archive path, source path relative to repo root); dspack.json is synthetic.
ENTRIES = [
    ("manifest.json", "manifest.json"),
    ("package.json", "package.json"),
    ("pnpm-workspace.yaml", "pnpm-workspace.yaml"),
    ("overrides/cordis.patch.yml", "overrides/cordis.patch.yml"),
]

# ── 内置 dsh-ops fork（v1.0.3-pre.2）──────────────────────────────────────────
#
# 为什么内置而不是 URL 依赖：
#   v1.0.3-pre.1 把 dsh-ops 写成 GitHub Releases 的 tgz URL，pnpm 安装时必须
#   直连 github.com。在 TLS 被代理拦截的机器上 Node 校验不了代理的根证书，
#   pnpm 在下载这个「直接依赖」时一行日志都没输出就崩溃（启动器记为
#   exit code 0xc0000409），整个整合包装不上。
#   本版把发布产物作为不可变输入放进仓库 vendor/，打包时校验 sha512 后展开到
#   dspack 的 overrides/dsh-ops/；launcher 安装完成后把 overrides/ 覆盖到 profile
#   根，profile 的 package.json 用 link:./dsh-ops 指向它 —— 安装期不访问 GitHub。
VENDOR_DIR = "vendor"
DSH_OPS_TGZ = "dsh-ops-0.4.1-dsh021.1.tgz"
# npm integrity（sha512, base64）——与 v1.0.3-pre.1 锁文件里的 dsh-ops 条目一致。
DSH_OPS_SHA512 = (
    "7oEJvHfswPLVdGyEnyOLJ+8Av9ixDniOeBZ6ut/dtDdrHqxk0xWC3foO0q8hPdcWruENdBc1B346Ju7DsrDyXQ=="
)
DSH_OPS_ARC_PREFIX = "overrides/dsh-ops"


def collect_vendor_entries(repo_root: Path) -> list[tuple[str, bytes]]:
    """Return (arcname, payload) for the vendored dsh-ops package tree.

    The tgz is the immutable fork release asset. Its sha512 is pinned here so a
    swapped or corrupted file fails the build instead of shipping silently.
    The archive's ``package/`` prefix is stripped, so the launcher's
    ``apply_overrides`` puts the tree at ``<profile>/dsh-ops/``.
    """
    tgz = repo_root / VENDOR_DIR / DSH_OPS_TGZ
    if not tgz.is_file():
        raise SystemExit(f"build-dspack: missing vendored package {tgz}")
    data = tgz.read_bytes()
    digest = base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")
    if digest != DSH_OPS_SHA512:
        raise SystemExit(
            f"build-dspack: sha512 mismatch for {tgz}\n"
            f"  expected {DSH_OPS_SHA512}\n  actual   {digest}"
        )
    out: list[tuple[str, bytes]] = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            name = member.name
            if not name.startswith("package/"):
                raise SystemExit(f"build-dspack: unexpected entry in {tgz}: {name}")
            rel = name[len("package/"):]
            if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
                raise SystemExit(f"build-dspack: unsafe entry in {tgz}: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise SystemExit(f"build-dspack: unreadable entry in {tgz}: {name}")
            out.append((f"{DSH_OPS_ARC_PREFIX}/{rel}", stream.read()))
    if not out:
        raise SystemExit(f"build-dspack: {tgz} contains no files")
    return out

# ── 依赖审计：第三方插件不得硬依赖 @deepseek-ai/dsh-* 核心包 ──────────────────
#
# 为什么必须挡住（v1.0.2 的事故复盘，见 docs/release-notes-v1.0.2.md）：
#   DSH 解析 bundle 是「两锚点」——**profile 的 node_modules 优先**，宿主安装目录兜底
#   （dsh-app-boot: "Pnpm-managed entries in the profile's node_modules resolve first"）。
#   于是任何一个依赖只要把核心包装进 profile，就会遮蔽宿主自带的同版本包；启动期兼容门禁
#   按「profile 里那份」的版本判定，版本与宿主不一致就整行 disable，并连带一串 pending
#   （v1.0.2 里是 storage-domain → workspace → workspace-controller →
#   directoryPickerController，工作区与目录选择器全废）。
#   v1.0.1 的元凶是暂屏蔽的 dsh-prompt@0.3.0 硬依赖 dsh-storage-domain@^0.2.0-rc.2；
#   这类引用本该写成 peerDependency（由宿主提供），所以打包期直接判红。
CORE_PACKAGE_PREFIX = "@deepseek-ai/dsh-"
# 这些 spec 形态不查 registry（git / 本地 / workspace 协议）。
UNQUERYABLE_SPEC_MARKERS = ("github:", "git+", "git:", "file:", "link:", "workspace:", "http")


def dependency_specs(manifest: dict) -> list:
    """Return (name, spec) pairs from the manifest's mirrored dependency map."""
    deps = manifest.get("dependencies") or {}
    return sorted((str(name), str(spec)) for name, spec in deps.items())


def declared_dependencies(name: str, spec: str) -> tuple:
    """Read one dependency's own dependencies map from the registry.

    Returns (deps, error). The error is a human-readable reason when the map
    cannot be read (offline, unknown package, timeout) so the caller can degrade
    to a warning instead of failing a build that would otherwise be fine.
    """
    if any(spec.startswith(marker) for marker in UNQUERYABLE_SPEC_MARKERS):
        return {}, None
    npm = shutil.which("npm")
    if npm is None:
        return {}, "npm not found on PATH"
    try:
        proc = subprocess.run(
            [npm, "view", name + "@" + spec, "dependencies", "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {}, type(error).__name__ + ": " + str(error)
    if proc.returncode != 0:
        lines = (proc.stderr or "").strip().splitlines()
        return {}, (lines[-1] if lines else "npm exit %d" % proc.returncode)
    raw = (proc.stdout or "").strip()
    if raw in ("", "{}", "undefined", "null"):
        return {}, None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        return {}, "unparsable npm output: %s" % error
    return (parsed if isinstance(parsed, dict) else {}), None


def audit_core_shadowing(manifest: dict) -> list:
    """Return one line per dependency that would shadow a host core package.

    A dependency declaring an @deepseek-ai/dsh-* entry in its "dependencies"
    (instead of "peerDependencies") makes pnpm place that core package in the
    profile's node_modules, where it wins module resolution over the host's own
    copy and can trip the startup compatibility gate.
    """
    violations = []
    unverified = []
    for name, spec in dependency_specs(manifest):
        declared, error = declared_dependencies(name, spec)
        if error is not None:
            unverified.append(name + "@" + spec + ": " + error)
            continue
        core = {k: v for k, v in declared.items() if k.startswith(CORE_PACKAGE_PREFIX)}
        if core:
            pinned = ", ".join(k + "@" + v for k, v in sorted(core.items()))
            violations.append(name + "@" + spec + " hard-depends on core package(s): " + pinned)
    for line in unverified:
        print("build-dspack: WARNING dependency audit skipped for " + line)
    if unverified:
        print(
            "build-dspack: WARNING dependency audit was incomplete (registry "
            "unreachable?) - the shadowing rule is unverified for the packages above."
        )
    return violations


# Directory (relative to repo root) whose contents are shipped verbatim under
# the same path inside the dspack. The launcher copies ``home/`` onto the
# DSH_HOME root on import, so ``home/skills/<name>`` lands at
# ``<DSH_HOME>/skills/<name>``.
HOME_PAYLOAD_DIR = "home"


def collect_home_entries(repo_root: Path) -> list[tuple[str, str]]:
    """Return (arcname, src_rel) pairs for every file under HOME_PAYLOAD_DIR.

    Raises SystemExit when the payload contains a nested ``home/`` tree —
    see :func:`_reject_nested_home`.
    """
    out: list[tuple[str, str]] = []
    base = repo_root / HOME_PAYLOAD_DIR
    if not base.is_dir():
        return out
    for p in sorted(base.rglob("*")):
        if p.is_file():
            rel = p.relative_to(repo_root).as_posix()
            out.append((rel, rel))
    _reject_nested_home(out)
    return out


def _reject_nested_home(entries: list[tuple[str, str]]) -> None:
    """Fail fast on nested ``home/`` directories inside the payload.

    An arcname shaped like ``home/**/home/**`` means a bundled skill was
    copied with its upstream host ``home/`` prefix still attached (issue #1):
    the launcher maps ``home/`` onto the DSH_HOME root on import, so the
    duplicate would land at ``<DSH_HOME>/skills/<name>/home/skills/<name>/``
    — dead data the skill filesystem never scans. Surface it at pack time
    instead of shipping it silently.
    """
    prefix = f"{HOME_PAYLOAD_DIR}/"
    inner = f"/{HOME_PAYLOAD_DIR}/"
    polluted = [
        arcname
        for arcname, _ in entries
        if arcname.startswith(prefix) and inner in arcname[len(prefix):]
    ]
    if not polluted:
        return
    shown = "\n".join(f"  - {arcname}" for arcname in polluted[:20])
    more = len(polluted) - 20
    raise SystemExit(
        f"build-dspack: {len(polluted)} payload file(s) live under a nested "
        "'home/' directory (e.g. home/skills/<name>/home/...). The launcher "
        "maps 'home/' onto the DSH_HOME root, so these would become dead "
        f"duplicates under <DSH_HOME>:\n{shown}"
        + (f"\n  ... and {more} more" if more > 0 else "")
        + "\nFix: remove the nested home/ tree(s), e.g. `git rm -r "
        "home/skills/<name>/home`. See docs/fix-plan-issue-1-v2.7.1.md."
    )


def build(repo_root: Path, out_dir: Path) -> tuple[Path, str]:
    manifest = json.loads((repo_root / "manifest.json").read_text(encoding="utf-8"))
    name = manifest["name"]
    version = manifest["version"]
    dspack_name = f"{name}-{version}.dspack"

    out_dir.mkdir(parents=True, exist_ok=True)
    dspack_path = out_dir / dspack_name

    # Collect (and validate) payload entries *before* touching the output
    # files, so a nested-home or bad-vendor rejection leaves no partial dspack.
    home_entries = collect_home_entries(repo_root)
    vendor_entries = collect_vendor_entries(repo_root)

    with zipfile.ZipFile(dspack_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("dspack.json", DSPACK_JSON)
        for arcname, src in ENTRIES:
            zf.writestr(arcname, (repo_root / src).read_bytes())
        for arcname, payload in vendor_entries:
            zf.writestr(arcname, payload)
        for arcname, src in home_entries:
            zf.writestr(arcname, (repo_root / src).read_bytes())

    digest = hashlib.sha256(dspack_path.read_bytes()).hexdigest()
    (out_dir / f"{dspack_name}.sha256").write_text(digest)  # 64 bytes, no newline

    return dspack_path, digest


def main() -> int:
    here = Path(__file__).resolve().parent
    repo_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else here.parent
    out_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path.cwd()

    manifest = json.loads((repo_root / "manifest.json").read_text(encoding="utf-8"))
    skip_audit = "--no-dep-audit" in sys.argv[3:] or os.environ.get("DSH_PACK_SKIP_DEP_AUDIT") == "1"
    if skip_audit:
        print("build-dspack: dependency audit skipped (--no-dep-audit / DSH_PACK_SKIP_DEP_AUDIT=1)")
    else:
        violations = audit_core_shadowing(manifest)
        if violations:
            raise SystemExit(
                "build-dspack: refusing to pack - these dependencies put a core @deepseek-ai/dsh-*\n"
                "package into the profile's node_modules, which shadows the host's own copy and can\n"
                "disable a whole row at startup (see docs/release-notes-v1.0.2.md):\n"
                + "\n".join("  - " + violation for violation in violations)
                + "\nFix: drop the plugin, or have upstream move that reference to peerDependencies."
                "\n     Do not paper over it with a pnpm override - that still leaves two copies of a core package."
            )
        print("build-dspack: dependency audit ok - no dependency shadows a core package")

    dspack_path, digest = build(repo_root, out_dir)
    size = dspack_path.stat().st_size
    print(f"built  {dspack_path}  ({size} bytes)")
    print(f"sha256 {digest}")
    print(f"sidecar {(out_dir / (dspack_path.name + '.sha256'))}")

    # Count skill directories: home/skills/<name>/... (not SKILL.md files —
    # a skill may legitimately ship nested SKILL.md files, and the old
    # `count("/") == 2` check could never match home/skills/<name>/SKILL.md,
    # so it always printed 0 even when all 47 skills were packed).
    skill_count = len({
        e[0].split("/")[2]
        for e in collect_home_entries(repo_root)
        if e[0].startswith("home/skills/") and len(e[0].split("/")) > 3
    })
    print(f"skills {skill_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
