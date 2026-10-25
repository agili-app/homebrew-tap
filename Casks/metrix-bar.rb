cask "metrix-bar" do
  version "0.0.1"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "64069b4728d6d6f5373b4bb51967e35e387312aa9d310cd58819c3b312730cbe"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-18/macos-arm64/Metrix.Bar-0.0.1-arm64.dmg"
    end
    on_intel do
      sha256 "da30c252d9ba6bdae2b9e3c51b3e7e9ec8cae6da7d3026e51ddb8f298943ab54"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-18/macos-x86_64/Metrix.Bar-0.0.1-amd64.dmg"
    end

    depends_on macos: :monterey

    app "Metrix.Bar.app"

    zap trash: [
      "~/Library/Application Support/bar.metrix",
      "~/Library/Caches/bar.metrix",
      "~/Library/Preferences/bar.metrix.plist",
      "~/Library/Saved Application State/bar.metrix.savedState",
    ]
  end

  on_linux do
    on_arm do
      sha256 "fb1c40bc57e807b08bb4e76726354308d9a7d23f5449ef4e781e7312484c1496"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-18/linux-arm64/metrix-bar-0.0.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "abc0e8ebb44f3a6035398d1675293d0befc508b9d9c96b642e3a786cf3122d55"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-18/linux-x86_64/metrix-bar-0.0.1-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
