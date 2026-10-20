cask "metrix-bar" do
  version "0.0.1"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "02a93de6cd0d67579e1826bd2b6cc7160128f6a4a76919c1e96cd8049179ad23"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-11/macos-arm64/Metrix.Bar-0.0.1-arm64.dmg"
    end
    on_intel do
      sha256 "e7ddf535ee01be7765ad528c85c1f3c3595e5f3d797989bd80cbb542e0e14ae7"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-11/macos-x86_64/Metrix.Bar-0.0.1-amd64.dmg"
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
      sha256 "662b96df992b30f94432cce9e1140a197c788a5398ba8d9200c6a4c103374053"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-11/linux-arm64/metrix-bar-0.0.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "056e545ece452fbe112a61b2d61ca1aaa6900df9e7624f94ba2f77c342dbb782"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-11/linux-x86_64/metrix-bar-0.0.1-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
