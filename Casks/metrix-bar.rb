cask "metrix-bar" do
  version "0.0.1"

  on_arm do
    sha256 "0216f882ba20ea5e9057a307cf9f8557e80b1b514cb243abe8fe3cc9004c495b"
    url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-7/macos-arm64/Metrix.Bar-0.0.1-arm64.dmg"
  end
  on_intel do
    sha256 "ba99682edbe8812ecf088df1061b205410c8cd2eefa037daca95cdaac1b06462"
    url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-7/macos-x86_64/Metrix.Bar-0.0.1-amd64.dmg"
  end
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
