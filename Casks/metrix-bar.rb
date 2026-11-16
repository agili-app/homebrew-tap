cask "metrix-bar" do
  version "0.2.6"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "1795eebb41b93517197f076bd2cc2a1286e4dd74eb1aace9be56c12c213a68ed"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.6/build-68/macos-arm64/metrix-bar-0.2.6-arm64.dmg"
    end
    on_intel do
      sha256 "ff4436578cb6e6c55e85061cb1fca69f3c46fb157d99162c308355cb8b0970e7"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.6/build-68/macos-x86_64/metrix-bar-0.2.6-amd64.dmg"
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
      sha256 "5005f0bbcf46fecc0d8517368efb864222d9c3f9d41e1177d6d38a68dad8cda9"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.6/build-68/linux-arm64/metrix-bar-0.2.6-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "e2dd076cf690cea2f9de9ce98099d38c4e8f443f7e038961058471b108f7a812"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.6/build-68/linux-x86_64/metrix-bar-0.2.6-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
