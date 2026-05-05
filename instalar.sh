#!/usr/bin/env bash
# ============================================================
#  YTDL-PRO — Script de instalação automática
#  Suporta: Linux, macOS, Windows (via Git Bash / WSL)
# ============================================================

set -e

VERMELHO='\033[0;31m'
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
CIANO='\033[0;36m'
BRANCO='\033[1;37m'
RESET='\033[0m'

echo ""
echo -e "${CIANO}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${CIANO}║         YTDL-PRO — Instalação Automática         ║${RESET}"
echo -e "${CIANO}╚══════════════════════════════════════════════════╝${RESET}"
echo ""

# Verificar Python
if ! command -v python3 &>/dev/null; then
    echo -e "${VERMELHO}❌  Python 3 não encontrado!${RESET}"
    echo -e "   Instale em: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${VERDE}✅  Python ${PYTHON_VERSION} encontrado${RESET}"

# Verificar pip
if ! command -v pip3 &>/dev/null && ! python3 -m pip --version &>/dev/null; then
    echo -e "${VERMELHO}❌  pip não encontrado!${RESET}"
    exit 1
fi
echo -e "${VERDE}✅  pip encontrado${RESET}"

# Verificar ffmpeg
if command -v ffmpeg &>/dev/null; then
    echo -e "${VERDE}✅  FFmpeg encontrado${RESET}"
else
    echo -e "${AMARELO}⚠   FFmpeg não encontrado${RESET}"
    echo ""
    
    OS=$(uname -s 2>/dev/null || echo "Windows")
    
    if [[ "$OS" == "Linux" ]]; then
        echo -e "${CIANO}   Instalando FFmpeg (Linux)...${RESET}"
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y ffmpeg
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y ffmpeg
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm ffmpeg
        else
            echo -e "${AMARELO}   Instale manualmente: https://ffmpeg.org/download.html${RESET}"
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        echo -e "${CIANO}   Instalando FFmpeg (macOS via Homebrew)...${RESET}"
        if command -v brew &>/dev/null; then
            brew install ffmpeg
        else
            echo -e "${AMARELO}   Instale Homebrew e depois: brew install ffmpeg${RESET}"
        fi
    else
        echo -e "${AMARELO}   Windows: Baixe em https://www.gyan.dev/ffmpeg/builds/${RESET}"
        echo -e "${AMARELO}   e adicione ao PATH do sistema.${RESET}"
    fi
fi

echo ""
echo -e "${CIANO}📦  Instalando ytdl-pro...${RESET}"
echo ""

# Instalar o pacote
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -e . --quiet

echo ""
echo -e "${VERDE}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${VERDE}║         ✅  YTDL-PRO INSTALADO COM SUCESSO!       ║${RESET}"
echo -e "${VERDE}╚══════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${BRANCO}  Como usar:${RESET}"
echo -e "  ${CIANO}ytdl-pro${RESET}                    → Menu interativo"
echo -e "  ${CIANO}ytdl-pro baixar URL${RESET}         → Baixar vídeo"
echo -e "  ${CIANO}ytdl-pro playlist URL${RESET}       → Baixar playlist"
echo -e "  ${CIANO}ytdl-pro historico${RESET}          → Ver histórico"
echo -e "  ${CIANO}ytdl-pro --help${RESET}             → Ajuda completa"
echo ""
echo -e "${AMARELO}  ⚠  Respeite os direitos autorais!${RESET}"
echo ""
