#!/usr/bin/env bash
# Hardware / tool check for running cbroll locally on macOS. Read-only: installs nothing.
ok() { printf "  \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }

echo "Система"
sw_vers 2>/dev/null | sed 's/^/  /' || warn "не macOS"
chip=$(sysctl -n machdep.cpu.brand_string 2>/dev/null)
[[ "$(uname -m)" == "arm64" ]] && ok "Apple Silicon ($chip)" || warn "Intel ($chip): сегментация и рендер будут медленнее"
mem=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1073741824 ))
(( mem >= 16 )) && ok "RAM ${mem} ГБ" || warn "RAM ${mem} ГБ — рекомендуется 16 ГБ (BiRefNet требует много памяти)"
free=$(df -g . | awk 'NR==2 {print $4}')
(( free >= 20 )) && ok "Свободно ${free} ГБ" || warn "Свободно ${free} ГБ — нужно ~20 ГБ (модели, node_modules, рендеры)"

echo "Инструменты"
for t in brew git python3 uv node npm ffmpeg ffprobe; do
  if command -v $t >/dev/null; then ok "$t: $($t --version 2>&1 | head -1)"; else warn "$t не найден"; fi
done
py=$(python3 -c 'import sys; print(sys.version_info >= (3, 11))' 2>/dev/null)
[[ "$py" == "True" ]] || warn "нужен Python 3.11+ (brew install python@3.12 или uv python install 3.12)"
nodev=$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
(( nodev >= 18 )) || warn "нужен Node.js 18+ (рекомендуется 20/22)"
echo
echo "Установка (когда всё зелёное): uv venv && uv pip install -e . && (cd renderer && npm ci)"
