#!/usr/bin/env bash
# 从产品 appcast 同步 Cask：解析最新 zip 的 version/url，下载算 sha256，回写 Casks/<token>.rb。
# 用法：update-cask.sh <token> <appcast-url>
#   ./update-cask.sh tinymd     https://downloads.agili.app/tinymd-app/appcast.xml
#   ./update-cask.sh metrix-bar https://downloads.agili.app/metrix-bar/appcast.xml
set -euo pipefail

token="${1:?usage: update-cask.sh <token> <appcast-url>}"
appcast="${2:?usage: update-cask.sh <token> <appcast-url>}"
cask_file="Casks/${token}.rb"

[ -f "$cask_file" ] || { echo "no such cask: $cask_file" >&2; exit 1; }

xml="$(curl -fsSL "$appcast")"

# 取第一个 item 的 shortVersionString 与 .zip enclosure url（跳过 .delta 增量包）
version="$(printf '%s' "$xml" | grep -oE '<sparkle:shortVersionString>[^<]+' | head -1 | sed 's/.*>//')"
url="$(printf '%s' "$xml" | grep -oE 'url="[^"]+\.zip"' | head -1 | sed 's/^url="//; s/"$//')"

[ -n "$version" ] || { echo "no sparkle:shortVersionString in appcast" >&2; exit 1; }
[ -n "$url" ]     || { echo "no .zip enclosure url in appcast" >&2; exit 1; }

# 已是最新（version 与 url 都一致）则跳过
if grep -q "version \"$version\"" "$cask_file" && grep -qF "$url" "$cask_file"; then
  echo "$token already at $version"
  exit 0
fi

sha256="$(curl -fsSL "$url" | shasum -a 256 | awk '{print $1}')"
echo "$token -> $version  $url  sha256:$sha256"

# 回写三行：version / sha256 / url
sed -i '' \
  -e "s|^  version \".*\"|  version \"$version\"|" \
  -e "s|^  sha256 \".*\"|  sha256 \"$sha256\"|" \
  -e "s|^  url \".*\"|  url \"$url\"|" \
  "$cask_file"

echo "updated $cask_file"
