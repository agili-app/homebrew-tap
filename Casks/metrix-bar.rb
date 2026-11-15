cask "metrix-bar" do
  version "0.2.5"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "db37799832dcb66dbec48a57336557e81bdcb2028a7d13a686b9eeb458b92852"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.5/build-63/macos-arm64/metrix-bar-0.2.5-arm64.dmg"
    end
    on_intel do
      sha256 "6dd3e9595be76afdc4f91d4cebe69ead6113e250e12d7f6965a945993a305481"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.5/build-63/macos-x86_64/metrix-bar-0.2.5-amd64.dmg"
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
      sha256 "3885bc1fbfcc33e65187bfc1410f5cfaff1d8d2db6d9c897a7e1926cf7aacce9"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.5/build-63/linux-arm64/metrix-bar-0.2.5-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "adbf5a4c47199912166747cd4c6ecc97dc7ce45763e1e8e1a466fbf1f8d7d221"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.5/build-63/linux-x86_64/metrix-bar-0.2.5-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
