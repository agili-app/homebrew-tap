cask "tinymd-cli" do
  version "0.1.6"

  name "TinyMD CLI"
  desc "A command-line tool for Markdown documents"
  homepage "https://tinymd.app"

  on_macos do
    on_arm do
      sha256 "f943c5086ad55be58d8043b9aa51d4ed1efc04b59ae5380b818a628aefff7e6f"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.6/build-49/macos-arm64/TinyMD-0.1.6-macos-arm64.dmg"
    end
    on_intel do
      sha256 "937bf59e6443225115720338f1ea1565a2e9e72616b66167cff4bf41d25fb6af"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.6/build-49/macos-x86_64/TinyMD-0.1.6-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    conflicts_with cask: "tinymd"

    binary "TinyMD.app/Contents/Helpers/tinymd"
  end

  on_linux do
    on_arm do
      sha256 "14b93be4872c202df24e8c748326e78a099ec557badcd9254528e1352b3d5c63"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.6/build-49/linux-arm64/TinyMD-0.1.6-linux-arm64-cli.tar.gz"
    end
    on_intel do
      sha256 "d900eeb0e39c541a9568c703bfbdbff158ab2b8baaee06e1f90a24cc415b1326"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.6/build-49/linux-x86_64/TinyMD-0.1.6-linux-x86_64-cli.tar.gz"
    end

    binary "tinymd"
  end
end
