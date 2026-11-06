cask "tinymd" do
  version "0.1.1"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd-app"

  on_macos do
    on_arm do
      sha256 "a3511d931e317abd8d402540402a14bb6925e66265551130af8ac7173d1f5137"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/macos-arm64/TinyMD-0.1.1-macos-arm64.dmg"
    end
    on_intel do
      sha256 "1de9e8fe9f70fc552545da501840f1262060ec87036818787e7f75ac3f924396"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/macos-x86_64/TinyMD-0.1.1-macos-x86_64.dmg"
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
      sha256 "7d9b843c6f32fdd8e2214ff44a1319962998af562e2bf947ea48c3b94d4bdc92"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/linux-arm64/TinyMD-0.1.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "5ee750e3be8031083df6a40183b00ca24291b7d7a7a952480da32bcd2d91ac23"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/linux-x86_64/TinyMD-0.1.1-linux-x86_64.tar.gz"
    end

    depends_on cask: "agili-app/tap/tinymd-cli"

    binary "TinyMD", target: "tinymd-app"
  end
end
