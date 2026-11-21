cask "metrix-bar" do
  version "0.3.1"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "48994004c7741d11e5244c9eb43248c4376e1d662937116bcbe9df194092cff4"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.1/build-78/macos-arm64/metrix-bar-0.3.1-arm64.dmg"
    end
    on_intel do
      sha256 "b955ebbe9501328aaaf430a9632d6c0f386bc7ed6247cc09b8cbdc754dc993fb"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.1/build-78/macos-x86_64/metrix-bar-0.3.1-amd64.dmg"
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
      sha256 "47cac9e8f79287b7502ce1c0fc49a5e10289f97c1346c51aefc1b17935dea940"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.1/build-78/linux-arm64/metrix-bar-0.3.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "cf780b2ec4f8dca6271875dfd2f0e8e2f035b6efb49f6db925b4230ca76da6ab"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.1/build-78/linux-x86_64/metrix-bar-0.3.1-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
