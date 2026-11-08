cask "tinymd" do
  version "0.1.2"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd-app"

  on_macos do
    on_arm do
      sha256 "d9ea95dacbf1cffdf077432f6036c0739b91178770bc4edb002bf6d7a196b203"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/macos-arm64/TinyMD-0.1.2-macos-arm64.dmg"
    end
    on_intel do
      sha256 "d53d52b7f693a230b02dd6dabc82bc026421e4c5b6b7476201e57f3ac2d6aacb"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/macos-x86_64/TinyMD-0.1.2-macos-x86_64.dmg"
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
      sha256 "ddfd353ce65e6dadec73e8bc875963b0f899d8a2d690d1a663ff788cda9d2e0f"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/linux-arm64/TinyMD-0.1.2-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "c9c360c63278e6a8f994759eb5e439c2b07d2345e597a75fe800830653410591"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/linux-x86_64/TinyMD-0.1.2-linux-x86_64.tar.gz"
    end

    depends_on cask: "agili-app/tap/tinymd-cli"

    binary "TinyMD", target: "tinymd-app"
  end
end
