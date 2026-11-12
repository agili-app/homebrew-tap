cask "metrix-bar" do
  version "0.2.1"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "c1963b7f0476f83ad0cc96711fc6068c1ad6d11b80d3156dda1fbd779b13bf79"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.1/build-46/macos-arm64/metrix-bar-0.2.1-arm64.dmg"
    end
    on_intel do
      sha256 "8b37778ed50647c5b0d09b89302d928f579bf6fdb18475bdf80a0c64fde3d65b"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.1/build-46/macos-x86_64/metrix-bar-0.2.1-amd64.dmg"
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
      sha256 "9e9d2daf7c871eaa1cedb8d3bcc9918b510835d022d0bfb3cbb723234ea44238"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.1/build-46/linux-arm64/metrix-bar-0.2.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "b8896e71f396d9a31569a46e17d278316b3c293fa9de06d293529975654487b7"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.2.1/build-46/linux-x86_64/metrix-bar-0.2.1-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
