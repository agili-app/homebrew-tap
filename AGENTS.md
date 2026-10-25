# Agili Homebrew Tap、Scoop Bucket 与发布流水线

这是独立 Git 仓库（在官网中作为 `tap/` 子模块），负责 TinyMD / Metrix.Bar 的公共发布、Homebrew Cask 与 Scoop 清单。产品构建契约在各源码仓库的 `docs/architecture/updates.md` / `docs/release.md`，安装说明见 `README.md`。

## 文档

- `README.md` 保持极简，以安装说明为主；日常开发尽量不修改，不添加内部发布、存储或维护细节。开发约定写入本文件。

## 验证

- 发布脚本依赖按 CI 锁文件安装：`python3 -m pip install --require-hashes -r scripts/release/requirements.lock`；使用隔离环境，CI Python 版本见 `.github/workflows/release.yml`。
- Python 语法检查：`python3 -c 'import ast,pathlib; files=list(pathlib.Path("scripts/release").glob("*.py")); [ast.parse(p.read_text(), filename=str(p)) for p in files]; print(f"checked {len(files)} scripts")'`，不导入或执行发布模块。
- `scripts/` 下不新增或保留测试脚本；验证使用语法检查与必要的临时离线检查，临时检查脚本放在仓库外。
- Cask 语法检查：`for cask in Casks/*.rb; do ruby -c "$cask" || exit; done`；修改后同时 `git diff --check`。这些检查不等于原生打包、签名或发布端到端验证。

## 标准源码构建契约

- 产品注册统一在 `scripts/release/common.py` 的 `PRODUCTS`：配置源码 `repo`、存储 `prefix`、`updater`（仅支持 `gpui` / `mygo`）与 GitHub secret/variable 的名称映射 `credentials`。注册信息和 `plan` 的 `credentials` JSON 输出只能含名称，不含凭据值；缺少的可选 profile 名称用空字符串。workflow 的 `product` 为字符串输入，由 CLI 按 registry 校验；不添加产品条件分支，不传入完整 `secrets`。
- 现有 secret/variable 名称保持不变。更新公钥、签名 identity、Apple team 和部署 webhook 取 GitHub variables；更新私钥、P12、P12 密码、notary 账号/密码和 profiles 取 secrets。TinyMD profiles 仍为 `PROVISIONING_PROFILE_APP_BASE64` / `PROVISIONING_PROFILE_PREVIEW_BASE64`，Metrix.Bar 不配置 profiles。
- `plan` 读取完整源码 SHA 对应的 `scripts/release/platforms.json`，构建 checkout 固定到该 SHA；`runs-on` 直接采用经过 `RUNNERS` 白名单验证的 `matrix.runner`，包括 `macos-26`，tap 不覆盖产品 runner。
- 同一 SHA 下必须提供 `scripts/release/setup/action.yml` composite action，inputs 为 `platform`、`arch`。源码 setup 负责 Go/Rust/Xcode 选择、系统依赖、公共工具安装与公共依赖缓存校验，引用的第三方 Action 必须锁完整 SHA，下载二进制校验 checksum。tap 已删除旧 `bootstrap.py` / `cache_guard.py`，对应职责迁入源码；setup/cache 不读取或安装发布凭据，不接收 R2 配置。
- 源码打包入口保持 `python scripts/release/build.py --platform PLATFORM --arch ARCH --update-version VERSION --display-version VERSION --build-seq SEQ --channel CHANNEL --output-dir ABSOLUTE_PATH`。源码负责原生打包、签名、profile 生命周期与 `artifacts.json`；tap 负责预留、baseline 下载、验证、stage 和公开索引。
- 构建统一接收 `RELEASE_UPDATE_PUBLIC_KEY` / `RELEASE_UPDATE_PRIVATE_KEY`；源码自行适配更新器旧变量或私钥临时文件，并在 `finally` 删除自己创建的私钥文件。`RELEASE_PROFILE_APP_BASE64` / `RELEASE_PROFILE_PREVIEW_BASE64` 只在 build step 提供，TinyMD 源码自行安装并在成功或失败后清理 profiles，Metrix.Bar 可忽略空值。
- `RELEASE_WORKSPACE` 是绝对 `.release-output` 路径。源码自行将 `CARGO_TARGET_DIR` / `GOCACHE` 等编译输出放在其中；不将源码、target、GOCACHE、私钥或私有日志写进公共 cache。允许缓存经源码 setup 验证的公共依赖下载，Rust Git 依赖和 Cargo credentials 不缓存，Go 只使用公开 proxy/sumdb，不允许私有模块或 credentialed fallback。
- `RELEASE_BASELINES_FILE` 是 tap 为每次 build 写入的绝对 UTF-8 JSON 临时文件，即使 baseline 为空也是数组；不使用 `RELEASE_BASELINES_JSON`。数组保留 baseline 的 `platform`、`arch`、`format`、`sha256`、`url`、`updateVersion`、绝对 `path` 及可选 `signaturePath` / `nativeManifest`。tap 在构建成功、失败或打包验证失败后通过 `finally` 删除该临时 JSON。
- 公共 workflow 的 `apple_signing.py prepare` / `always()` cleanup 只管理临时 Apple keychain 和 notary profile，不接收 product，也不安装 provisioning profiles。源码可读取 `MACOS_SIGNING_IDENTITY`、`DEVELOPMENT_TEAM`、`SIGNING_KEYCHAIN_NAME`、`MACOS_NOTARY_KEYCHAIN_PROFILE` 和 `MACOS_NOTARY_KEYCHAIN`。
- R2 配置仅注入实际访问存储的 plan/build/publish、包管理器同步、webhook 状态检查和 cleanup steps。builder 再从源码 subprocess 环境中剥离 `R2_*`、`*_TOKEN`、P12、原始 notary 凭据与旧 profile 变量，保留源码所需的标准 `RELEASE_PROFILE_*` 及更新凭据。
- 每个产品的 `artifacts.json` 必须包含 `buildSeq`，类型严格为整数（不能是布尔值、浮点数或字符串），范围 `1..99990000`，且等于 reservation；MyGO 原生 manifest 同样校验。GPUI/TinyMD feed 增加大小写固定的 `buildSeq` 字段；现有两种更新协议继续各自适配，未知协议明确拒绝。TinyMD 完整包的 Minisign trusted comment 可带 `build:<seq>`；tap 按原始签名字节保存和传递，不解析或重写 comment，源码与客户端负责签名语义校验。
- 启用新调度前，先让两个产品源码具备上述 setup/build 契约；首次发布选择包含这些改动的完整源码 SHA，旧源码 SHA 不兼容新 workflow。TinyMD 首个迁移版本须提升 SemVer，让旧客户端先获得 buildSeq 更新能力；不要仅给历史 feed 补序号并继续引用没有 `build:<seq>` 绑定的旧签名。
- 应用内更新按各产品客户端协议支持同版本高 `buildSeq`，Scoop 版本使用 `displayVersion.buildSeq` 支持同版 rebuild。Homebrew Cask 继续只使用 `displayVersion`，同版 rebuild 虽更新 URL/hash，也可能不被 Homebrew 识别为新版；本次不调整 Homebrew 版本策略。
- 接入同类产品时登记 registry、在源码提交 setup/build/platforms 契约实现，并配置映射的 secrets/variables；标准构建 workflow 无需新分支。Homebrew/Scoop 的安装描述、文件与产品特殊安装行为继续在各自配置中显式添加；使用新更新协议需先扩展并审核 adapter。保留 stable rebuild 显式开关、不可变 build 路径、版本/序号单调规则与单产品串行锁。

## 发布边界

- 入口是 `.github/workflows/release.yml` 的手动 `workflow_dispatch`；未经明确发版要求，不触发它，也不直接运行 publisher、builder、源码 bootstrap 或 sync_cask 来做验证。
- `publisher.py plan` 会预留版本并写 R2 状态，并非 dry-run；build 上传 stage，publish 推进公开索引，webhook 触发站点重建，`sync_cask.py` 会同步 Homebrew 与 Scoop 清单。
- 保留按 product 串行且 `cancel-in-progress: false` 的锁；源码锁定完整 SHA；禁止 rerun 或复用 reservation，失败后必须新建 `workflow_dispatch` 发布任务。
- stable 发布也推进 preview feed，直接复用 `stable/` 路径的正式包、签名与 delta；已有更高版本或 buildSeq 的 preview 不回退，也不阻塞 stable 发布。preview 单独发布只推进 preview，可显式使用与 stable 相同的基础版本。失败的 stable 版本可在新任务中同版发布，使用新 buildSeq 与不可变路径；已成功的 stable 同版发布必须显式启用 rebuild。
- 私有 stage 仅用于同次运行跨 job 交接，不复用签名包；cleanup job 在成功或失败后删除当前 run 的私有包。失败诊断日志保存到私有存储的 `debug/{product}/{run_id}/{platform}-{arch}/private-build.log`，不由 cleanup 或 plan 清理；由 R2 的 `debug/` 生命周期规则在七天后删除。后续新任务的 plan 删除同产品其他旧 run 的残留 stage；不删除 control 或其他产品数据。
- 源码仓库负责原生打包、签名与 `artifacts.json`；本仓库负责版本预留、上传、feed、Cask 与重建通知。不要给某一产品另造平行发布链。
- TinyMD 正式版同步同时更新 `tinymd`、`tinymd-app` 与 `tinymd-cli`；`tinymd` 同时安装 App 和 CLI，与仅 App 的 `tinymd-app` 在所有平台互斥。macOS 下 `tinymd` 与仅 CLI 的 `tinymd-cli` 双向互斥，CLI 复用签名 DMG 中的 `TinyMD.app/Contents/Helpers/tinymd`，`tinymd` 从安装后的 App 链接 CLI；Linux 下 `tinymd` 安装 GUI 并依赖 `agili-app/tap/tinymd-cli`，两者可共存，GUI 通过 `tinymd-app` 启动。`tinymd-app` 与 `tinymd-cli` 在两个平台均可共存；Linux 仅使用 tar.gz 的 arm64/x86_64 资产，`tinymd` 只支持 GUI 与 CLI 的架构交集，无交集时保留为仅 macOS。
- Scoop 清单由 `scripts/release/sync_scoop.py` 从 stable 的 Windows exe 元数据生成到 `bucket/`，版本为 `displayVersion.buildSeq`，使同版 rebuild 仍可升级。TinyMD 提供 App+CLI、仅 App、仅 CLI 三个入口，主包只使用 GUI/CLI 架构交集，无可用架构时失败且不写半套清单；支持 arm64 与 x86_64（Scoop `64bit`）。Metrix.Bar 通过 URL `#/dl.7z` 解包 NSIS，不执行安装器，数据保留在应用默认 AppData 位置。
- stable 的 `sync_cask.py` 在隔离 checkout 中读取同一份最新 stable，同次提交 Cask 与 Scoop，沿用 fetch/regenerate/retry；preview 不同步。Scoop 不设置 checkver/autoupdate，URL/hash 只取发布元数据，许可证使用 Proprietary。官方清单 schema 与解包行为参考 https://github.com/ScoopInstaller/Scoop ，核对 commit `e6aa3b366bdee8ed138c1e0f7b85192ebdd35d0f` 的 `schema.json`、`lib/decompress.ps1`。
- 保留不可变 release 路径、签名与 updateVersion 绑定、状态及公开索引一致性；平台签名不能替代 payload / delta 验签。
- 公共 CI 不上传私有源码、私钥或编译缓存；依赖缓存仅允许固定 SHA 源码 setup 验证通过的公共目录，保留第三方 Action 的完整 SHA 锁定与 Python hash 锁文件。
- `.private-source/`、`.release-output/`、工具、缓存、报告与本地凭据按 `.gitignore` 排除，不写入日志或 Git。
- 本仓库提交与官网子模块指针更新是两个独立操作；不要在官网普通改动中顺带推进发布仓库指针。
