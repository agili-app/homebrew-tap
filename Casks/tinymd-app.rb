cask "tinymd-app" do
  version "0.0.1"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd"

  on_macos do
    on_arm do
      sha256 "13128ea5eed031ffe7f9a585ba3c106d66af1406286370c8135d83fcbb552cc9"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/macos-arm64/TinyMD-0.0.1-macos-arm64.dmg"
    end
    on_intel do
      sha256 "3f020b386fb5163519c971fc4ee402468068c99c68c51be7c51de54705b6e9f2"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/macos-x86_64/TinyMD-0.0.1-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    app "TinyMD.app"

    zap trash: [
      "~/Library/Application Support/app.tinymd.TinyMD",
      "~/Library/Caches/app.tinymd.TinyMD",
      "~/Library/Preferences/app.tinymd.TinyMD.plist",
      "~/Library/Saved Application State/app.tinymd.TinyMD.savedState",
    ]
  end

  on_linux do
    on_arm do
      sha256 "af9083ca99a5dc8f5f62e74fa81b00fd064985885e295a95e4a78aca922e16d7"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/linux-arm64/TinyMD-0.0.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "6c8b3b3e7be900f728958d6529359c7083cdc126909c52183ca6730d1730c448"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/linux-x86_64/TinyMD-0.0.1-linux-x86_64.tar.gz"
    end

    binary "TinyMD", target: "tinymd-app"
  end
end
