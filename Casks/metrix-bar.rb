cask "metrix-bar" do
  version "0.2.4"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "4192ef4ea96da8ce4cd5caf214053a1d77b9f71241c577d2e4d7a0eefd485a09"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.4/build-58/macos-arm64/metrix-bar-0.2.4-arm64.dmg"
    end
    on_intel do
      sha256 "dd075404b90e055be6f27b7fb37f0233bbef1c80793d60ea5ff049d1dab5bd45"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.4/build-58/macos-x86_64/metrix-bar-0.2.4-amd64.dmg"
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
      sha256 "8fee978b275a84a23dd11369fff476b5384eaac634e3c5984fd4d6c27eb8995f"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.4/build-58/linux-arm64/metrix-bar-0.2.4-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "e7f29f596062c2c5b593a30df10945daea143443f37f9b9851033e266e0f86fb"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.4/build-58/linux-x86_64/metrix-bar-0.2.4-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
