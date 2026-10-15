cask "tinymd-cli" do
  version "0.0.1"
  sha256 "d94a5ab8cd2fecb09a6bc8d5b7982c53d0b9cb72cf4e4a04bbf1a1801659d012"

  url "https://downloads.agili.app/tinymd-app/releases/0.0.1/build-7/macos-universal/TinyMD-0.0.1-macos-universal.dmg"
  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
  depends_on macos: :sequoia

  binary "TinyMD.app/Contents/Helpers/tinymd"
end
