cask "tinymd-cli" do
  version "0.0.1"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

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

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "90fff61a1d2cbc3240ab1a66430903e6def825c1498d5756e73118b07dec9ece"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-14/linux-arm64/TinyMD-0.0.1-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "691f450485a974370d12f1f9768e5114140d63ee87e8bdbfca557721843c6951"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-14/linux-x86_64/TinyMD-0.0.1-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
