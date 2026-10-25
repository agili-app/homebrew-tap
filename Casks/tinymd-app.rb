cask "tinymd-app" do
  version "0.0.1"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd"

  on_macos do
    on_arm do
      sha256 "f61194799aa08c247ce47625d005fb335013eb87a2d11c6d73275c83cb4356c2"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-14/macos-arm64/TinyMD-0.0.1-macos-arm64.dmg"
    end
    on_intel do
      sha256 "cda48d800d2524bc2855d2efeea131ee7fd4fb3dd4d7c67143a5aea53fc616be"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-14/macos-x86_64/TinyMD-0.0.1-macos-x86_64.dmg"
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
      sha256 "8838f9544d5b92928b22667f2e02175850846fb811f2a0913279c27a4ffe6297"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-14/linux-arm64/TinyMD-0.0.1-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "6d679a83e58f8cefef7f5e401fe487e4522712b9d52cb87520ffc3412bafaa0d"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-14/linux-x86_64/TinyMD-0.0.1-linux-x86_64.tar.gz"
    end

    binary "TinyMD", target: "tinymd-app"
  end
end
