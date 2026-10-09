cask "tinymd" do
  version "0.0.1"
  sha256 "1ec344721642b363d7cc934b4a23808063d03a43c05647f6a0f46f7bc1d7dc3a"

  url "https://downloads.agili.app/tinymd-app/releases/#{version}/10.6ef18d92fcb2693a/TinyMD-#{version}.zip"
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
