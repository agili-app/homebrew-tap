cask "metrix-bar" do
  version "0.0.1"
  sha256 "02676a75211430c6a9f0ea4cd204eef0e0292d5180dd148168ffa09010f284dc"

  url "https://downloads.agili.app/releases/#{version}/10.6ef18d92fcb2693a/Metrix.Bar-#{version}.dmg"
  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://agili.app"

  depends_on macos: ">= 26.0"
  auto_updates true

  app "Metrix.Bar.app"

  zap trash: [
    "~/Library/Application Support/bar.metrix",
    "~/Library/Caches/bar.metrix",
    "~/Library/Preferences/bar.metrix.plist",
    "~/Library/Saved Application State/bar.metrix.savedState",
  ]
end
