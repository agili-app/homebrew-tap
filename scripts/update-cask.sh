#!/usr/bin/env bash
# 从产品 appcast 同步 Cask：取最新 item 的 zip version/url，下载算 sha256，回写 Casks/<token>.rb。
# 用法：update-cask.sh <token> <appcast-url>
#   ./update-cask.sh tinymd     https://downloads.agili.app/tinymd-app/appcast.xml
#   ./update-cask.sh metrix-bar https://downloads.agili.app/metrix-bar/appcast.xml
set -euo pipefail

token="${1:?usage: update-cask.sh <token> <appcast-url>}"
appcast="${2:?usage: update-cask.sh <token> <appcast-url>}"
cask_file="Casks/${token}.rb"

[ -f "$cask_file" ] || { echo "no such cask: $cask_file" >&2; exit 1; }

# 用 ruby 的 REXML 解析 appcast，取 sparkle:version 最大的 item 的 zip url 与展示版本，
# 避免"第一个 item 就是最新"的假设，也精确排除 .delta 增量包。
read -r version url < <(
  curl -fsSL "$appcast" | ruby -rrexml/document -e '
    doc = REXML::Document.new(STDIN.read)
    item = doc.get_elements("//item").max_by do |i|
      i.elements["sparkle:version"]&.text.to_i
    end
    enc = item&.elements&.detect { |e| e.name == "enclosure" && e.attributes["url"]&.end_with?(".zip") }
    ver = item&.elements&.[]("sparkle:shortVersionString")&.text
    abort "no zip enclosure" unless enc && ver
    puts "#{ver} #{enc.attributes["url"]}"
  '
)

# version/url 都已是最新则跳过（幂等）
if grep -q "version \"$version\"" "$cask_file" && grep -qF "$url" "$cask_file"; then
  echo "$token already at $version"
  exit 0
fi

sha256="$(curl -fsSL "$url" | shasum -a 256 | awk '{print $1}')"
echo "$token -> $version  $url  sha256:$sha256"

# ruby 写回三行，跨 GNU/macOS 一致，无需 sed -i 平台差异
ruby -e '
  f = ARGV[0]
  s = File.read(f)
  s.sub!(/^  version ".*"/,  %(  version "#{ARGV[1]}"))
  s.sub!(/^  sha256 ".*"/,   %(  sha256 "#{ARGV[2]}"))
  s.sub!(/^  url ".*"/,      %(  url "#{ARGV[3]}"))
  File.write(f, s)
' "$cask_file" "$version" "$sha256" "$url"

echo "updated $cask_file"
