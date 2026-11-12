cask "metrix-bar" do
  version "0.2.2"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "4331720e62882e58cdf0379af44af24c70e69b6088dfa69613a2060e94bbeb59"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.2/build-51/macos-arm64/metrix-bar-0.2.2-arm64.dmg"
    end
    on_intel do
      sha256 "24f145a83a6644d12fc759b5e8da3fe52f3c2ecef627eb204577f1ae601fb46f"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.2/build-51/macos-x86_64/metrix-bar-0.2.2-amd64.dmg"
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
      sha256 "4ece3ae37e1541a770f566f14468b472a209b5e328504198b191934644016db6"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.2/build-51/linux-arm64/metrix-bar-0.2.2-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "e355f1d36702f52be3b4811eb240645f01406312133cc6a12eec673c7d3ee42f"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.2/build-51/linux-x86_64/metrix-bar-0.2.2-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
