cask "metrix-bar" do
  version "0.0.1"
  sha256 "fd838487c2b948d0b7cc2d4c1d7e6d581f40f217a8cb9b0948ed5d71d83e1609"

  url "https://downloads.agili.app/metrix-bar/releases/0.0.1/macos-universal/Metrix.Bar%200.0.1.dmg"
  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://agili.app"

  depends_on macos: :monterey
  auto_updates true

  app "Metrix.Bar.app"

  zap trash: [
    "~/Library/Application Support/bar.metrix",
    "~/Library/Caches/bar.metrix",
    "~/Library/Preferences/bar.metrix.plist",
    "~/Library/Saved Application State/bar.metrix.savedState",
  ]
end
