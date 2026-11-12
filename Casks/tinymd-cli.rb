cask "tinymd-cli" do
  version "0.1.4"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  on_macos do
    on_arm do
      sha256 "39efcc7e40bf263f8ef9a1c5e9fcc922b0934f8bf24424f3d64c68ad88f46370"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/macos-arm64/TinyMD-0.1.4-macos-arm64.dmg"
    end
    on_intel do
      sha256 "6761218e6c66a9b7a6856c1e32cb2e72148948dd5104672ee7ca8154a8a30f84"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/macos-x86_64/TinyMD-0.1.4-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "25812043f0d0d2b3c64496ba80f4ca2e99cc42b1ca6f96429ef71ac47be515e2"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/linux-arm64/TinyMD-0.1.4-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "4ae98d0e75c646ec9c5df2e3f37b20a2b15314f94d7431f674ea921ee85500e7"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/linux-x86_64/TinyMD-0.1.4-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
