cask "metrix-bar" do
  version "0.0.1"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "0216f882ba20ea5e9057a307cf9f8557e80b1b514cb243abe8fe3cc9004c495b"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-7/macos-arm64/Metrix.Bar-0.0.1-arm64.dmg"
    end
    on_intel do
      sha256 "ba99682edbe8812ecf088df1061b205410c8cd2eefa037daca95cdaac1b06462"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-7/macos-x86_64/Metrix.Bar-0.0.1-amd64.dmg"
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
      sha256 "0b0a6af4459fc783dd749c2c49e0e6a9941450e06b2ea49c5a35f6e73b299ef7"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-7/linux-arm64/metrix-bar-0.0.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "986125b851553593c7f81b4795c3dec3cd6782ce22f1e3ad94bc6565c72bb3e8"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.0.1/build-7/linux-x86_64/metrix-bar-0.0.1-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
