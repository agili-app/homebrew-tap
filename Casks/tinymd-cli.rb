cask "tinymd-cli" do
  version "0.1.0"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

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

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "df55119784068b821ad92835a1bd13b31bca9d2a6bc7e417e1f7454bf70b0323"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.0/build-28/linux-arm64/TinyMD-0.1.0-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "a09a0e8d2241da39e46fdee055d3201f5cdf045220108eeb01b5abe6c2751549"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.0/build-28/linux-x86_64/TinyMD-0.1.0-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
