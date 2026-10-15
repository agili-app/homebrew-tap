# Agili Homebrew Tap 与发布流水线

这是独立 Git 仓库（在官网中作为 `tap/` 子模块），负责 TinyMD / Metrix.Bar 的公共发布与 Cask。产品构建契约在各源码仓库的 `docs/architecture/updates.md` / `docs/release.md`，安装说明见 `README.md`。

## 文档

- `README.md` 保持极简，以安装说明为主；日常开发尽量不修改，不添加内部发布、存储或维护细节。开发约定写入本文件。

## 验证

- 发布脚本依赖按 CI 锁文件安装：`python3 -m pip install --require-hashes -r scripts/release/requirements.lock`；使用隔离环境，CI Python 版本见 `.github/workflows/release.yml`。
- Python 语法检查：`python3 -c 'import ast,pathlib; files=list(pathlib.Path("scripts/release").glob("*.py")); [ast.parse(p.read_text(), filename=str(p)) for p in files]; print(f"checked {len(files)} scripts")'`，不导入或执行发布模块。
- `scripts/` 下不新增或保留测试脚本；验证使用语法检查与必要的临时离线检查，临时检查脚本放在仓库外。
- Cask 语法检查：`for cask in Casks/*.rb; do ruby -c "$cask" || exit; done`；修改后同时 `git diff --check`。这些检查不等于原生打包、签名或发布端到端验证。

## 发布边界

- 入口是 `.github/workflows/release.yml` 的手动 `workflow_dispatch`；未经明确发版要求，不触发它，也不直接运行 publisher、builder、bootstrap 或 sync_cask 来做验证。
- `publisher.py plan` 会预留版本并写 R2 状态，并非 dry-run；build 上传 stage，publish 推进公开索引，webhook 触发站点重建，`sync_cask.py` 会改 Cask。
- 保留按 product 串行且 `cancel-in-progress: false` 的锁；源码锁定完整 SHA；禁止 rerun 或复用 reservation，失败后必须新建 `workflow_dispatch` 发布任务。
- stable 与 preview 独立推进，可显式使用相同基础版本；stable 不更新 preview。失败的 stable 版本可在新任务中同版发布，使用新 buildSeq 与不可变路径；已成功的 stable 同版发布必须显式启用 rebuild。
- 私有 stage 仅用于同次运行跨 job 交接，不复用签名包；cleanup job 在成功或失败后删除当前 run 的私有包和诊断。后续新任务的 plan 删除同产品其他旧 run 的残留 stage；不删除 control 或其他产品数据。
- 源码仓库负责原生打包、签名与 `artifacts.json`；本仓库负责版本预留、上传、feed、Cask 与重建通知。不要给某一产品另造平行发布链。
- TinyMD 正式版同步同时更新 `tinymd`、`tinymd-app` 与 `tinymd-cli`；前两个安装同一 App 并互斥，CLI 复用签名 DMG 中的 `TinyMD.app/Contents/Helpers/tinymd`，可与 App 共存。
- 保留不可变 release 路径、签名与 updateVersion 绑定、状态及公开索引一致性；平台签名不能替代 payload / delta 验签。
- 公共 CI 不上传私有源码、私钥或编译缓存；依赖缓存仅允许 workflow 与 `cache_guard.py` 认可的公共目录，保留第三方 Action 的完整 SHA 锁定与 Python hash 锁文件。
- `.private-source/`、`.release-output/`、工具、缓存、报告与本地凭据按 `.gitignore` 排除，不写入日志或 Git。
- 本仓库提交与官网子模块指针更新是两个独立操作；不要在官网普通改动中顺带推进发布仓库指针。
