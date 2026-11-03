cask "metrix-bar" do
  version "0.1.0"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "3a07a0081d43f24cbe4fdc5cc956f4ff6b2b31ce7ff0e714387516c891652268"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.0/build-28/macos-arm64/metrix-bar-0.1.0-arm64.dmg"
    end
    on_intel do
      sha256 "1e85e17d4b02feaffc64e087c82eaaebbc89c6448a83274a0145f14f4351a337"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.0/build-28/macos-x86_64/metrix-bar-0.1.0-amd64.dmg"
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
      sha256 "db1c93fede4268445393dd7b995d071a4dd75c93c58a09d3ef54d7d133a8f8e8"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.0/build-28/linux-arm64/metrix-bar-0.1.0-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "9a49e2ba0ff230d1c532d5ff8314dd550003c7c636fda492b7ff6f3f7c71f625"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.0/build-28/linux-x86_64/metrix-bar-0.1.0-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
