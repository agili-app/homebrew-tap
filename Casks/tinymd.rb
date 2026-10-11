cask "tinymd" do
  version "0.0.1"
  sha256 "dc864967fe71e3fb1606c0944125df6872e9ef71977032c2ee3c4d85b46831d1"

  url "https://downloads.agili.app/tinymd-app/releases/0.0.1/11.3b26d1ac9eeb1dff/TinyMD-0.0.1.zip"
  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://agili.app"

  # macOS 15.3+ required; Homebrew only models whole releases, so :sequoia (>= 15.0)
  # is the closest valid floor. The 15.0–15.2 window is narrowed by the app's own
  # LSMinimumSystemVersion on launch.
  depends_on macos: :sequoia
  auto_updates true

  app "TinyMD.app"

  zap trash: [
    "~/Library/Application Support/app.tinymd.TinyMD",
    "~/Library/Caches/app.tinymd.TinyMD",
    "~/Library/Preferences/app.tinymd.TinyMD.plist",
    "~/Library/Saved Application State/app.tinymd.TinyMD.savedState",
  ]
end
