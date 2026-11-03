cask "tinymd" do
  version "0.1.0"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd-app"

  on_macos do
    on_arm do
      sha256 "18faa15116794d5b4816f6dd936bee4bf012ab21f4654f945830275c59ccbf1e"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.0/build-28/macos-arm64/TinyMD-0.1.0-macos-arm64.dmg"
    end
    on_intel do
      sha256 "57379d2daa9cce5dead8aa1e14084d7470e7bc24b5d43be17eb5b39199ebb0ff"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.0/build-28/macos-x86_64/TinyMD-0.1.0-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd-cli"

    app "TinyMD.app"
    binary "#{appdir}/TinyMD.app/Contents/Helpers/tinymd"

    zap trash: [
      "~/Library/Application Support/app.tinymd.TinyMD",
      "~/Library/Caches/app.tinymd.TinyMD",
      "~/Library/Preferences/app.tinymd.TinyMD.plist",
      "~/Library/Saved Application State/app.tinymd.TinyMD.savedState",
    ]
  end

  on_linux do
    on_arm do
      sha256 "97dd98d62214acab107771ffac918775202bffe82299600508f2219b0c141293"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.0/build-28/linux-arm64/TinyMD-0.1.0-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "fe13bf3354161f452211ed5e85e400b8a69ce372441154b5547a93bb4b188eda"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.0/build-28/linux-x86_64/TinyMD-0.1.0-linux-x86_64.tar.gz"
    end

    depends_on cask: "agili-app/tap/tinymd-cli"

    binary "TinyMD", target: "tinymd-app"
  end
end
