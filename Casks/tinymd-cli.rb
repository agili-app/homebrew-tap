cask "tinymd-cli" do
  version "0.0.1"

  on_arm do
    sha256 "13128ea5eed031ffe7f9a585ba3c106d66af1406286370c8135d83fcbb552cc9"
    url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/macos-arm64/TinyMD-0.0.1-macos-arm64.dmg"
  end
  on_intel do
    sha256 "3f020b386fb5163519c971fc4ee402468068c99c68c51be7c51de54705b6e9f2"
    url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/macos-x86_64/TinyMD-0.0.1-macos-x86_64.dmg"
  end
  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
  depends_on macos: :sequoia
  conflicts_with cask: "tinymd"

  binary "TinyMD.app/Contents/Helpers/tinymd"
end
