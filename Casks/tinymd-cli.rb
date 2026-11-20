cask "tinymd-cli" do
  version "0.1.7"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  on_macos do
    on_arm do
      sha256 "f7c1fbc685634c528d2defcab056fc75b52f746a79426eb094fe875db6fc1b28"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.7/build-51/macos-arm64/TinyMD-0.1.7-macos-arm64.dmg"
    end
    on_intel do
      sha256 "87353bd5f985b6b068e14cfd842a853fb4cfb006a584650aaa825e033bb04313"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.7/build-51/macos-x86_64/TinyMD-0.1.7-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "b489cc95485c9b70223d9e7240a6b1d7214af2846f2e41680a3bd63b7b6da557"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.7/build-51/linux-arm64/TinyMD-0.1.7-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "0a88463ea72e9b8b1fbd3185917bb25994f531640489491b38471e5de29c2101"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.7/build-51/linux-x86_64/TinyMD-0.1.7-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
