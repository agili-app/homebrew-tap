cask "metrix-bar" do
  version "0.0.1"
  sha256 "ff8fdceb43d347924cc7ee7e832746e37e5e72c2bcad3bd78304bfa50d689dc8"

  url "https://downloads.agili.app/metrix-bar/releases/0.0.1/14.3151d1ebaa395f16/Metrix.Bar-0.0.1.zip"
  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://agili.app"

  # macOS 26+ required; :tahoe is the release symbol for macOS 26.
  depends_on macos: :tahoe
  auto_updates true

  app "Metrix.Bar.app"

  zap trash: [
    "~/Library/Application Support/bar.metrix",
    "~/Library/Caches/bar.metrix",
    "~/Library/Preferences/bar.metrix.plist",
    "~/Library/Saved Application State/bar.metrix.savedState",
  ]
end
