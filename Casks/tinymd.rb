cask "tinymd" do
  version "0.0.1"
  sha256 "2143eaa825c7709f1ba0d2906fcf146a6070dd82f58ff3a7687fc667fec5f927"

  url "https://downloads.agili.app/tinymd-app/releases/0.0.1/macos-universal/TinyMD-0.0.1-macos-universal.dmg"
  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://agili.app"

  # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
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
