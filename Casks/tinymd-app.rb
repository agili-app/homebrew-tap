cask "tinymd-app" do
  version "0.1.5"

  name "TinyMD"
  desc "A minimal Markdown editor"
  homepage "https://tinymd.app"

  auto_updates true
  conflicts_with cask: "tinymd"

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
      sha256 "f1215f6ba1f36c4c9f48a8dc97f31caf876db47f91b2799d630c204aa44992d3"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.5/build-48/linux-arm64/TinyMD-0.1.5-linux-arm64.tar.gz"
    end
    on_intel do
      sha256 "0399db39118226edc8c6bee2b9a50d84167589fe21693bd2b919ded5f474a94a"
      url "https://downloads.agili.app/stable/tinymd-app/releases/0.1.5/build-48/linux-x86_64/TinyMD-0.1.5-linux-x86_64.tar.gz"
    end

    binary "TinyMD", target: "tinymd-app"
  end
end
