cask "metrix-bar" do
  version "0.3.2"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "ccc74b0a0daad501d1e16d44fe6acafff7fdbcd13ea3fa2c4a45eddfcaf387c9"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.2/build-79/macos-arm64/metrix-bar-0.3.2-arm64.dmg"
    end
    on_intel do
      sha256 "9be658609bd5360dffaab2cdda622d5b89ddef63d76c1e59a3cfe7b70b60fac1"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.2/build-79/macos-x86_64/metrix-bar-0.3.2-amd64.dmg"
    end

    depends_on macos: :ventura

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
      sha256 "ab4a58b4d6e81668f7a557024a2ed8e2da1c4b6711c581523fb433e60f50f216"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.2/build-79/linux-arm64/metrix-bar-0.3.2-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "024179a6a64fd02a24fd6d29704fe4651fd62749fcf3c64d1f4a7cd38e82f1e9"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.2/build-79/linux-x86_64/metrix-bar-0.3.2-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
