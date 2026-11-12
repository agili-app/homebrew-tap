cask "metrix-bar" do
  version "0.2.0"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "0ffa2441b643f69596375676a2c74cf34e902ecd51a54cdd46b5482433065c4e"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.0/build-45/macos-arm64/metrix-bar-0.2.0-arm64.dmg"
    end
    on_intel do
      sha256 "ab6c3a2c94e2aa7a00f4e50b5b7633ae6ce58b65d6f16adf9599bd679d5aa3bd"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.0/build-45/macos-x86_64/metrix-bar-0.2.0-amd64.dmg"
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
      sha256 "4ecdaaa6c1d85364cb23e608845e43369d9c2b10eb2b6372aace2f75c45ac960"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.0/build-45/linux-arm64/metrix-bar-0.2.0-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "3332d98ac029a07ae7cc49ea75a30bf902e742d8aeb5833782fda15915188178"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.0/build-45/linux-x86_64/metrix-bar-0.2.0-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
