cask "metrix-bar" do
  version "0.3.4"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "6cc7a4a2021a5a856aa25665a381bc88b6e41cf0c6f07bf47109a69571a3059a"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.4/build-92/macos-arm64/metrix-bar-0.3.4-arm64.dmg"
    end
    on_intel do
      sha256 "3df71b87fe771002a547b1f251b35b8224608b3008a917ab22e0792771f17ff5"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.4/build-92/macos-x86_64/metrix-bar-0.3.4-amd64.dmg"
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
      sha256 "072d50897cdd4f8de1007d97fd54156e511390b6a41112055a1bcdc0b9984dd3"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.4/build-92/linux-arm64/metrix-bar-0.3.4-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "e53908df164ead655c56f693c690aca4c601ae920208dbc129b35684cad6f7fd"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.4/build-92/linux-x86_64/metrix-bar-0.3.4-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
