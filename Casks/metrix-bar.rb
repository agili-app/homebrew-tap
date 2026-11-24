cask "metrix-bar" do
  version "0.3.3"

  name "Metrix.Bar"
  desc "A minimal menu bar metrics monitor"
  homepage "https://metrix.bar"

  auto_updates true

  on_macos do
    on_arm do
      sha256 "1dcb66710f8882e51a5bd6c8f37dbdb9c9f8d43fe524a81852d6212ad95780ca"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.3/build-88/macos-arm64/metrix-bar-0.3.3-arm64.dmg"
    end
    on_intel do
      sha256 "816db31d27940d94fa9c86fc60c33aef5c0bfb6e452d93d9bf2d52a11782bcba"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.3/build-88/macos-x86_64/metrix-bar-0.3.3-amd64.dmg"
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
      sha256 "a16771f92e6fcae8dc70ae75abc9f06912942e36cce30a092c35a9dadc869d00"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.3/build-88/linux-arm64/metrix-bar-0.3.3-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "bc879ce2d693761af44a57585a295b1f0de91fbdc2aefd200bb0678876c0bce1"
      url "https://downloads.agili.app/stable/metrix-bar/releases/0.3.3/build-88/linux-x86_64/metrix-bar-0.3.3-linux-amd64.tar.gz"
    end

    binary "metrix-bar"
  end
end
