cask "metrix-bar" do
  version "0.1.2"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "5ccff9e106d9953c36b53a5d7c1f0def8b42bb6381a0dea2997a37823ff1f17a"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.2/build-37/macos-arm64/metrix-bar-0.1.2-arm64.dmg"
    end
    on_intel do
      sha256 "43e1a1b0e418bf3245eb2babef8b8f458c1cc6356e358f995c464965b892332f"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.2/build-37/macos-x86_64/metrix-bar-0.1.2-amd64.dmg"
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
      sha256 "5cc936a62222238ff0a58bb34bcb21de48aad37445bf92ccb94b2b0807da5846"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.2/build-37/linux-arm64/metrix-bar-0.1.2-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "05b575e7ef5398a3c864ba0300661a3d9caf7d1b2960a3ec7f9c382054a67322"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.2/build-37/linux-x86_64/metrix-bar-0.1.2-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
