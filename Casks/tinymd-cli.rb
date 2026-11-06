cask "tinymd-cli" do
  version "0.1.1"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  on_macos do
    on_arm do
      sha256 "a3511d931e317abd8d402540402a14bb6925e66265551130af8ac7173d1f5137"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/macos-arm64/TinyMD-0.1.1-macos-arm64.dmg"
    end
    on_intel do
      sha256 "1de9e8fe9f70fc552545da501840f1262060ec87036818787e7f75ac3f924396"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/macos-x86_64/TinyMD-0.1.1-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "800d4aeb32813f54bd3bb74de95a619f992b0d7cd5630e1cbce9e49dd59f288f"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/linux-arm64/TinyMD-0.1.1-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "2a3f4a513992c601513f23775b2277a8a248ef59feea022f5460e3df806355a4"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.1/build-31/linux-x86_64/TinyMD-0.1.1-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
