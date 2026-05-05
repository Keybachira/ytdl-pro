# YTDL-PRO 🎬

> Downloader profissional de vídeos e playlists do YouTube com interface TUI incrível

```
 ██╗   ██╗████████╗██████╗ ██╗      ██████╗ ██████╗  ██████╗
 ╚██╗ ██╔╝╚══██╔══╝██╔══██╗██║     ██╔══██╗██╔══██╗██╔═══██╗
  ╚████╔╝    ██║   ██║  ██║██║     ██████╔╝██████╔╝██║   ██║
   ╚██╔╝     ██║   ██║  ██║██║     ██╔═══╝ ██╔══██╗██║   ██║
    ██║      ██║   ██████╔╝███████╗██║     ██║  ██║╚██████╔╝
    ╚═╝      ╚═╝   ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝
```

## ✨ Funcionalidades

| Feature | Detalhe |
|---------|---------|
| 🎬 Formatos | MP4 (vídeo) com suporte a MKV, MP3, FLAC |
| 🎯 Qualidade | Perfis predefinidos + resolução exata (144p → 4K) |
| 📋 Playlists | Download completo com subpasta automática |
| 🔢 Numeração | `01 - Título.mp4` na ordem original da playlist |
| ⚡ Paralelo | Threads configuráveis (1 a 16 simultâneas) |
| 🔄 Retomada | Downloads interrompidos retomam automaticamente |
| 🔍 Duplicatas | Verifica antes de baixar e pergunta o que fazer |
| 🖼 Thumbnails | Embutidas no arquivo + arquivo separado |
| 📝 Metadados | Título, canal, data embutidos no arquivo |
| 📜 Legendas | Português (automáticas + manuais) |
| 🍪 Cookies | Chrome, Firefox, Edge, Opera, arquivo .txt |
| 📊 Histórico | Registro completo de todos os downloads |
| ⚙️ Config | config.json + variáveis de ambiente (.env) |
| 👤 Perfis | Múltiplos perfis (Padrão, Econômico, Ultra HD, Áudio) |
| 🖥 Interface | Menu TUI + barra de progresso animada completa |
| 🌍 Cross-platform | Windows, Linux, macOS |

---

## 🚀 Instalação

### Via pip (recomendado)

```bash
pip install ytdl-pro
```

### Em modo desenvolvimento

```bash
git clone https://github.com/ytdl-pro/ytdl-pro
cd ytdl-pro
pip install -e .
```

### Dependência obrigatória: FFmpeg

**Linux (Debian/Ubuntu):**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Baixe em https://www.gyan.dev/ffmpeg/builds/ e adicione ao PATH.

---

## 🎮 Como Usar

### Menu interativo (recomendado)

```bash
ytdl-pro
# ou
ytdl
```

### Comandos diretos

```bash
# Baixar um vídeo
ytdl-pro baixar "https://youtube.com/watch?v=..."

# Baixar vídeo em qualidade específica
ytdl-pro baixar "URL" --qualidade 720

# Baixar vídeo em pasta específica
ytdl-pro baixar "URL" --pasta ~/Videos

# Baixar apenas áudio
ytdl-pro baixar "URL" --formato mp3

# Baixar playlist completa
ytdl-pro playlist "https://youtube.com/playlist?list=..."

# Baixar intervalo da playlist (vídeos 5 a 20)
ytdl-pro playlist "URL" --inicio 5 --fim 20

# Ver histórico de downloads
ytdl-pro historico

# Limpar histórico
ytdl-pro historico --limpar

# Ver configuração atual
ytdl-pro config --mostrar

# Resetar configuração
ytdl-pro config --reset
```

---

## ⚙️ Configuração

### Arquivo de configuração

O arquivo fica em `~/.config/ytdl-pro/config.json` e é criado automaticamente no primeiro uso.

Principais configurações:

```json
{
  "pasta_destino": "~/Downloads/ytdl-pro",
  "qualidade_padrao": "1080",
  "formato": "mp4",
  "threads": 4,
  "retomar": true,
  "legendas": true,
  "idioma_legendas": "pt",
  "thumbnails": true,
  "metadados": true,
  "subpasta_playlist": true,
  "limite_velocidade": null,
  "proxy": null
}
```

### Variáveis de ambiente

O arquivo `.env` fica em `~/.config/ytdl-pro/.env`:

```env
YTDL_PASTA=~/Downloads/ytdl-pro
YTDL_QUALIDADE=1080
YTDL_THREADS=4
YTDL_PROXY=http://usuario:senha@proxy:8080
YTDL_VELOCIDADE=5M
YTDL_COOKIES=chrome
YTDL_COOKIES_FILE=/caminho/para/cookies.txt
```

---

## 👤 Perfis

O YTDL-PRO vem com 4 perfis pré-configurados:

| Perfil | Qualidade | Threads | Uso |
|--------|-----------|---------|-----|
| **Padrão** | 1080p | 4 | Uso geral |
| **Econômico** | 480p | 2 | Economizar espaço/banda |
| **Ultra HD** | 4K | 6 | Máxima qualidade |
| **Áudio** | MP3 320k | 4 | Só áudio |

Gerencie perfis pelo menu `4. Gerenciar Perfis` ou crie seus próprios.

---

## 🍪 Vídeos Privados / Com Restrição

Para baixar vídeos privados ou com restrição de idade, configure cookies:

```bash
# Via menu interativo
ytdl-pro  # → opção 6 (Cookies / Auth)

# Ou direto no config
# Navegadores suportados: chrome, firefox, edge, opera, safari, brave, chromium
```

---

## 📊 Informações Exibidas Durante Download

- 🎬 Título e canal do vídeo
- ⏱ Duração total
- 🎯 Qualidade e formato selecionados
- 🔢 Progresso na playlist (ex: 3 de 15)
- 📊 Velocidade em MB/s
- 💾 Tamanho baixado / total
- ⏳ Tempo estimado restante (ETA)
- ✅ Histórico da sessão (concluídos, erros, pulados)

---

## 📁 Estrutura de Arquivos

```
~/Downloads/ytdl-pro/
├── Nome da Playlist/
│   ├── 01 - Título do Vídeo 1.mp4
│   ├── 01 - Título do Vídeo 1.pt.vtt    ← legenda
│   ├── 01 - Título do Vídeo 1.jpg       ← thumbnail
│   ├── 02 - Título do Vídeo 2.mp4
│   └── ...
└── Video Avulso.mp4

~/.config/ytdl-pro/
├── config.json    ← configurações
├── perfis.json    ← perfis de download
├── historico.json ← histórico de downloads
└── .env           ← variáveis de ambiente
```

---

## ⚠️ Aviso Legal

Este software é para uso pessoal e educacional. Respeite os direitos autorais e os Termos de Serviço do YouTube. Use apenas para baixar conteúdo que você tem permissão de baixar.

---

## 📦 Dependências

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Motor de download
- [rich](https://github.com/Textualize/rich) — Interface TUI
- [click](https://click.palletsprojects.com) — CLI
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Variáveis de ambiente
- [mutagen](https://mutagen.readthedocs.io) — Metadados de áudio
- [questionary](https://github.com/tmbo/questionary) — Prompts interativos
- [FFmpeg](https://ffmpeg.org) — Processamento de vídeo/áudio

---

## 📄 Licença

MIT License — veja [LICENSE](LICENSE)
