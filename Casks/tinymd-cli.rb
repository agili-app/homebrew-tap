cask "tinymd-cli" do
  version "0.1.2"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  on_macos do
    on_arm do
      sha256 "d9ea95dacbf1cffdf077432f6036c0739b91178770bc4edb002bf6d7a196b203"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/macos-arm64/TinyMD-0.1.2-macos-arm64.dmg"
    end
    on_intel do
      sha256 "d53d52b7f693a230b02dd6dabc82bc026421e4c5b6b7476201e57f3ac2d6aacb"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/macos-x86_64/TinyMD-0.1.2-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "fa7ec5ee366ec59a3c26d1b382b877df8d9ef9606906bfddc4e1062eb0152aca"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/linux-arm64/TinyMD-0.1.2-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "79ddf4d00530d285a45aba3a5018ad3ea424df453ec2a7d0275916253c6d85f9"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.2/build-36/linux-x86_64/TinyMD-0.1.2-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
