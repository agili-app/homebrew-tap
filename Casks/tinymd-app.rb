cask "tinymd-app" do
  version "0.1.4"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd"

  on_macos do
    on_arm do
      sha256 "39efcc7e40bf263f8ef9a1c5e9fcc922b0934f8bf24424f3d64c68ad88f46370"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/macos-arm64/TinyMD-0.1.4-macos-arm64.dmg"
    end
    on_intel do
      sha256 "6761218e6c66a9b7a6856c1e32cb2e72148948dd5104672ee7ca8154a8a30f84"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/macos-x86_64/TinyMD-0.1.4-macos-x86_64.dmg"
    end

    # macOS 15.3 required; Homebrew allows 15.0+, but macOS <15.3 is rejected by LSMinimumSystemVersion on launch.
    depends_on macos: :sequoia

    app "TinyMD.app"

    zap trash: [
      "~/Library/Application Support/app.tinymd.TinyMD",
      "~/Library/Caches/app.tinymd.TinyMD",
      "~/Library/Preferences/app.tinymd.TinyMD.plist",
      "~/Library/Saved Application State/app.tinymd.TinyMD.savedState",
    ]
  end

  on_linux do
    on_arm do
      sha256 "e6c98ebdfeaee4e3c920e803b00068b4163fa2d34521ea470000cb20e475f313"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/linux-arm64/TinyMD-0.1.4-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "ca5700abc02469652bbcb150cc5ee77d915cf5699cdf21b0e6ca0d357e9ca450"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.4/build-47/linux-x86_64/TinyMD-0.1.4-linux-x86_64.tar.gz"
    end

    binary "TinyMD", target: "tinymd-app"
  end
end
