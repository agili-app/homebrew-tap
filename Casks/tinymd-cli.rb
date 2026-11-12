cask "tinymd-cli" do
  version "0.1.5"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  on_macos do
    on_arm do
      sha256 "07cacfe34028a840bd45e46aa56189c18bb3ed38bdf1b9b64735433b591e1918"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.5/build-48/macos-arm64/TinyMD-0.1.5-macos-arm64.dmg"
    end
    on_intel do
      sha256 "5db12accf653ef865a6d8b01da5eeb42a555e76f5b78326301b61317aa06f4b2"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.5/build-48/macos-x86_64/TinyMD-0.1.5-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "ea6f1868613c3a9bf9539b5cbd3dd9aeb9b9235c85cb8fc93334c144d8d86629"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.5/build-48/linux-arm64/TinyMD-0.1.5-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "902ec3a68b28d933b31a2f1fb12b6683cf1b5f30665d03aa0beb43db9f83eaea"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.5/build-48/linux-x86_64/TinyMD-0.1.5-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
