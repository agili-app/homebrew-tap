cask "metrix-bar" do
  version "0.3.0"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "7ec04723de1dc44b7f72be946fe9bc24222d7fc2c1e281593a4f9eebaf93bac8"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.0/build-77/macos-arm64/metrix-bar-0.3.0-arm64.dmg"
    end
    on_intel do
      sha256 "e7566fd752ebc819ce972ce902ff730e7c934fd9de9ede64a191fa47a970047f"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.0/build-77/macos-x86_64/metrix-bar-0.3.0-amd64.dmg"
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
      sha256 "25de67446962916cbd0cf0b6b4d1b8962d43250b8b177a49de263fff8f086936"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.0/build-77/linux-arm64/metrix-bar-0.3.0-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "9ace2b2dc02283461d2ffeca8976a66aab6f584a3b93e58fb827c383652f3a0c"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.0/build-77/linux-x86_64/metrix-bar-0.3.0-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
