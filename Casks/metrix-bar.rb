cask "metrix-bar" do
  version "0.0.1"
  sha256 "f765647e815e7f9b3394d030d673726fa13f4ee960e01d3961a62ea2cea12fa3"

  url "https://downloads.agili.app/metrix-bar/releases/#{version}/13.5c557dc9d0e17789/Metrix.Bar-#{version}.zip"
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
