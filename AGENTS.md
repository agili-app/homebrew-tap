# Agili Homebrew Tap、Scoop Bucket 与发布流水线

这是独立 Git 仓库（在官网中作为 `tap/` 子模块），负责 TinyMD / Metrix.Bar 的公共发布、Homebrew Cask 与 Scoop 清单。产品构建契约在各源码仓库的 `docs/architecture/updates.md` / `docs/release.md`，安装说明见 `README.md`。

## 文档

- `README.md` 保持极简，以安装说明为主；日常开发尽量不修改，不添加内部发布、存储或维护细节。开发约定写入本文件。

## 验证

- 发布脚本依赖按 CI 锁文件安装：`python3 -m pip install --require-hashes -r scripts/release/requirements.lock`；使用隔离环境，CI Python 版本见 `.github/workflows/release.yml`。
- Python 语法检查：`python3 -c 'import ast,pathlib; files=list(pathlib.Path("scripts/release").glob("*.py")); [ast.parse(p.read_text(), filename=str(p)) for p in files]; print(f"checked {len(files)} scripts")'`，不导入或执行发布模块。
- `scripts/` 下不新增或保留测试脚本；验证使用语法检查与必要的临时离线检查，临时检查脚本放在仓库外。
- Cask 语法检查：`for cask in Casks/*.rb; do ruby -c "$cask" || exit; done`；修改后同时 `git diff --check`。这些检查不等于原生打包、签名或发布端到端验证。

## 发布边界

- 入口是 `.github/workflows/release.yml` 的手动 `workflow_dispatch`；未经明确发版要求，不触发它，也不直接运行 publisher、builder、bootstrap 或 sync_cask 来做验证。
- `publisher.py plan` 会预留版本并写 R2 状态，并非 dry-run；build 上传 stage，publish 推进公开索引，webhook 触发站点重建，`sync_cask.py` 会同步 Homebrew 与 Scoop 清单。
- 保留按 product 串行且 `cancel-in-progress: false` 的锁；源码锁定完整 SHA；禁止 rerun 或复用 reservation，失败后必须新建 `workflow_dispatch` 发布任务。
- stable 发布也推进 preview feed，直接复用 `stable/` 路径的正式包、签名与 delta；已有更高版本或 buildSeq 的 preview 不回退，也不阻塞 stable 发布。preview 单独发布只推进 preview，可显式使用与 stable 相同的基础版本。失败的 stable 版本可在新任务中同版发布，使用新 buildSeq 与不可变路径；已成功的 stable 同版发布必须显式启用 rebuild。
- 私有 stage 仅用于同次运行跨 job 交接，不复用签名包；cleanup job 在成功或失败后删除当前 run 的私有包。失败诊断日志保存到私有存储的 `debug/{product}/{run_id}/{platform}-{arch}/private-build.log`，不由 cleanup 或 plan 清理；由 R2 的 `debug/` 生命周期规则在七天后删除。后续新任务的 plan 删除同产品其他旧 run 的残留 stage；不删除 control 或其他产品数据。
- 源码仓库负责原生打包、签名与 `artifacts.json`；本仓库负责版本预留、上传、feed、Cask 与重建通知。不要给某一产品另造平行发布链。
- TinyMD 正式版同步同时更新 `tinymd`、`tinymd-app` 与 `tinymd-cli`；`tinymd` 同时安装 App 和 CLI，与仅 App 的 `tinymd-app` 在所有平台互斥。macOS 下 `tinymd` 与仅 CLI 的 `tinymd-cli` 双向互斥，CLI 复用签名 DMG 中的 `TinyMD.app/Contents/Helpers/tinymd`，`tinymd` 从安装后的 App 链接 CLI；Linux 下 `tinymd` 安装 GUI 并依赖 `agili-app/tap/tinymd-cli`，两者可共存，GUI 通过 `tinymd-app` 启动。`tinymd-app` 与 `tinymd-cli` 在两个平台均可共存；Linux 仅使用 tar.gz 的 arm64/x86_64 资产，`tinymd` 只支持 GUI 与 CLI 的架构交集，无交集时保留为仅 macOS。
- Scoop 清单由 `scripts/release/sync_scoop.py` 从 stable 的 Windows exe 元数据生成到 `bucket/`，版本为 `displayVersion.buildSeq`，使同版 rebuild 仍可升级。TinyMD 提供 App+CLI、仅 App、仅 CLI 三个入口，主包只使用 GUI/CLI 架构交集，无可用架构时失败且不写半套清单；支持 arm64 与 x86_64（Scoop `64bit`）。Metrix.Bar 通过 URL `#/dl.7z` 解包 NSIS，不执行安装器，数据保留在应用默认 AppData 位置。
- stable 的 `sync_cask.py` 在隔离 checkout 中读取同一份最新 stable，同次提交 Cask 与 Scoop，沿用 fetch/regenerate/retry；preview 不同步。Scoop 不设置 checkver/autoupdate，URL/hash 只取发布元数据，许可证使用 Proprietary。官方清单 schema 与解包行为参考 https://github.com/ScoopInstaller/Scoop ，核对 commit `e6aa3b366bdee8ed138c1e0f7b85192ebdd35d0f` 的 `schema.json`、`lib/decompress.ps1`。
- 保留不可变 release 路径、签名与 updateVersion 绑定、状态及公开索引一致性；平台签名不能替代 payload / delta 验签。
- 公共 CI 不上传私有源码、私钥或编译缓存；依赖缓存仅允许 workflow 与 `cache_guard.py` 认可的公共目录，保留第三方 Action 的完整 SHA 锁定与 Python hash 锁文件。
- `.private-source/`、`.release-output/`、工具、缓存、报告与本地凭据按 `.gitignore` 排除，不写入日志或 Git。
- 本仓库提交与官网子模块指针更新是两个独立操作；不要在官网普通改动中顺带推进发布仓库指针。
