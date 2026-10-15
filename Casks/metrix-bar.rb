cask "metrix-bar" do
  version "0.0.1"
  sha256 "02076474c66d73cff19d15937a4748951109e39934d04e09d54042cecb83a7c7"

  url "https://downloads.agili.app/metrix-bar/releases/0.0.1/build-6/macos-universal/Metrix.Bar-0.0.1.dmg"
  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

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
