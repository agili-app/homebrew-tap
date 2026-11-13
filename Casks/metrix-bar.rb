cask "metrix-bar" do
  version "0.2.3"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "65dc882f2ad01ecb38d70c1fe2066f20354e7b43a414e110e9aaee6996c4e97e"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.3/build-56/macos-arm64/metrix-bar-0.2.3-arm64.dmg"
    end
    on_intel do
      sha256 "3f516269623b7023f47abc975def9091eba096b6a8c54ff6c73ded9fada8b3bd"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.3/build-56/macos-x86_64/metrix-bar-0.2.3-amd64.dmg"
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
      sha256 "4c9366eda5ae1f8fa608188ffbec00cced9b0d8e4fa2863fa87dfbb7b8fe3ba2"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.3/build-56/linux-arm64/metrix-bar-0.2.3-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "d02e8473e90a3ded7ed86fe34b15eef6a272a5f6bb2cfcaa4ad22b05df266149"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.3/build-56/linux-x86_64/metrix-bar-0.2.3-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
