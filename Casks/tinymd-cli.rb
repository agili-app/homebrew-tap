cask "tinymd-cli" do
  version "0.0.1"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

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

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "a49a5d95e5efe95037a4ea6d6f0da148b0ea664bb0ac77528191043db649700e"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/linux-arm64/TinyMD-0.0.1-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "2cd99c4bb576baf341897d57ff2867c12b8efb9e60b8b0bde8c7488c4b85df61"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.0.1/build-8/linux-x86_64/TinyMD-0.0.1-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
