cask "tinymd" do
  version "0.0.1"
  sha256 "f06701cc96ae67bd27910158e5fac3a296933e31dac6b60f65cbb59f5671a8b2"

  url "https://downloads.agili.app/releases/#{version}/10.6ef18d92fcb2693a/TinyMD-#{version}.dmg"
  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://agili.app"

  depends_on macos: ">= 15.3"
  auto_updates true

  app "TinyMD.app"

  zap trash: [
    "~/Library/Application Support/app.tinymd.TinyMD",
    "~/Library/Caches/app.tinymd.TinyMD",
    "~/Library/Preferences/app.tinymd.TinyMD.plist",
    "~/Library/Saved Application State/app.tinymd.TinyMD.savedState",
  ]
end
