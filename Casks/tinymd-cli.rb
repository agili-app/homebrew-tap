cask "tinymd-cli" do
  version "0.1.3"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

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

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "8a9d106cc64643b95df0fbbd933fe3358b1bd4161f3b75a4ada1b75885de3b9a"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.3/build-43/linux-arm64/TinyMD-0.1.3-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "a8fd487fe66afa1daf0bfb90fd13a823cd8e92ca53c4f4b50e428cdae507e030"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.3/build-43/linux-x86_64/TinyMD-0.1.3-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
