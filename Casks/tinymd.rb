cask "tinymd" do
  version "0.1.7"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd-app"

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
      sha256 "e5660042a559ba86b0c4d67a2659da2614560b61655141ba1fef24449d7ad64a"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.7/build-51/linux-arm64/TinyMD-0.1.7-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "4469d3f5fe00c5fd1615167ad5b6b3298503f294406861166048c7155cb80284"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.7/build-51/linux-x86_64/TinyMD-0.1.7-linux-x86_64.tar.gz"
    end

    depends_on cask: "agili-app/tap/tinymd-cli"

    binary "TinyMD", target: "tinymd-app"
  end
end
