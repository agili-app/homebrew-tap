cask "tinymd" do
  version "0.1.3"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd-app"

  on_macos do
    on_arm do
      sha256 "1600f6e6a2929dc4899a74c927ea528274d1c89e426edc7df7294a8fd710d2c4"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.3/build-43/macos-arm64/TinyMD-0.1.3-macos-arm64.dmg"
    end
    on_intel do
      sha256 "002907c74f628b5305cd00fc9f6882952527b15ba6216212aed0d9f47236cc84"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.3/build-43/macos-x86_64/TinyMD-0.1.3-macos-x86_64.dmg"
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
      sha256 "3dc588b8cfe1983919b0865cb50e3cb6682dcb1e37782ab1722583541de215e7"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.3/build-43/linux-arm64/TinyMD-0.1.3-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "2b9c22a6fec2d0e7468d683446907c142f658a4bc59b562c56942bb04ec862e1"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.3/build-43/linux-x86_64/TinyMD-0.1.3-linux-x86_64.tar.gz"
    end

    depends_on cask: "agili-app/tap/tinymd-cli"

    binary "TinyMD", target: "tinymd-app"
  end
end
