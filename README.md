# Agili Packages

[Agili](https://agili.app) 应用的 Homebrew tap 和 Scoop bucket。

支持 macOS 和 Linux；Linux 下通过 `tinymd-app` 启动 TinyMD，通过 `metrix-bar` 启动 Metrix.Bar。

## Homebrew

```bash
brew install --cask agili-app/tap/tinymd      # TinyMD App 和 CLI
brew install --cask agili-app/tap/tinymd-app  # 仅 TinyMD App
brew install --cask agili-app/tap/tinymd-cli  # 仅 TinyMD CLI
brew install --cask agili-app/tap/metrix-bar  # Metrix.Bar
```

或先 `brew tap agili-app/tap` 再 `brew install --cask tinymd`。

## Scoop（Windows）

```powershell
scoop bucket add agili https://github.com/agili-app/homebrew-tap
scoop install agili/tinymd      # TinyMD App 和 CLI
scoop install agili/tinymd-app  # 仅 TinyMD App
scoop install agili/tinymd-cli  # 仅 TinyMD CLI
scoop install agili/metrix-bar  # Metrix.Bar
```
