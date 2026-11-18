cask "tinymd" do
  version "0.1.6"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd-app"

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

    conflicts_with cask: "tinymd-cli"

    app "TinyMD.app"
    binary "#{appdir}/TinyMD.app/Contents/Helpers/tinymd"

    zap trash: [
      "~/Library/Application Support/app.tinymd.TinyMD",
      "~/Library/Caches/app.tinymd.TinyMD",
      "~/Library/Preferences/app.tinymd.TinyMD.plist",
      "~/Library/Saved Application State/app.tinymd.TinyMD.savedState",
    ]
  end

  on_linux do
    on_arm do
      sha256 "549d86f0a3a308ae2aa0428edf99fb123339adb1003824322d90607ad232097d"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.6/build-49/linux-arm64/TinyMD-0.1.6-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "9546a6a3a01b243bf3c4280490274a0b8958ab148c3672886ea54eaf1e1b4cc3"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.6/build-49/linux-x86_64/TinyMD-0.1.6-linux-x86_64.tar.gz"
    end

    depends_on cask: "agili-app/tap/tinymd-cli"

    binary "TinyMD", target: "tinymd-app"
  end
end
