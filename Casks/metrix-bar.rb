cask "metrix-bar" do
  version "0.1.1"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "364441169f5c92f57a916670ba8e6956713d39d74b512665ac8daeeec24c6a16"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.1/build-34/macos-arm64/metrix-bar-0.1.1-arm64.dmg"
    end
    on_intel do
      sha256 "e94ae6226ae109f34d014e325343fd8bc5309a87c501cd48d03a699a0147b29b"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.1/build-34/macos-x86_64/metrix-bar-0.1.1-amd64.dmg"
    end

    depends_on macos: :monterey

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
      sha256 "ba8fe67e0c1c6df5f82eaa0413b5e1ac8e28aca01907c969dada602d4d7388de"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.1/build-34/linux-arm64/metrix-bar-0.1.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "c7ca6ff380c6f2c75896a9192ad4f2a0dd27b9b24de295928263a57eaadfb855"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.1.1/build-34/linux-x86_64/metrix-bar-0.1.1-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
