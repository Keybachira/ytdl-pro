# 🚀 GUIA COMPLETO DE INSTALAÇÃO — YTDL-PRO

## PASSO 1 — Instalar Python 3.9+

### Windows
1. Acesse: https://www.python.org/downloads/
2. Baixe o instalador (Python 3.11 recomendado)
3. ✅ MARQUE "Add Python to PATH" na instalação
4. Conclua a instalação

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

### macOS
```bash
brew install python3
```

---

## PASSO 2 — Instalar FFmpeg (OBRIGATÓRIO)

### Windows
1. Acesse: https://www.gyan.dev/ffmpeg/builds/
2. Baixe "ffmpeg-release-essentials.zip"
3. Extraia para C:\ffmpeg
4. Adicione C:\ffmpeg\bin ao PATH do Windows:
   - Pesquise "Variáveis de Ambiente" no Windows
   - Em "Path" → Novo → C:\ffmpeg\bin
5. Reinicie o terminal e teste: `ffmpeg -version`

### Linux
```bash
sudo apt install ffmpeg -y
```

### macOS
```bash
brew install ffmpeg
```

---

## PASSO 3 — Instalar o YTDL-PRO

### Opção A — Usando o script automático (Linux/macOS)
```bash
cd ytdl-pro
chmod +x instalar.sh
./instalar.sh
```

### Opção B — Manual (todos os sistemas)
```bash
cd ytdl-pro
pip install -e .
```

### Opção C — Instalar direto sem clonar
```bash
pip install yt-dlp rich python-dotenv questionary click mutagen requests Pillow
```

---

## PASSO 4 — Usar o YTDL-PRO

### Abrir o menu interativo
```bash
ytdl-pro
```

### Comandos diretos
```bash
# Baixar um vídeo
ytdl-pro baixar "https://youtube.com/watch?v=XXXXXXXXXXX"

# Baixar em qualidade específica
ytdl-pro baixar "URL" --qualidade 720

# Baixar em pasta específica
ytdl-pro baixar "URL" --pasta ~/Meus\ Videos

# Baixar como MP3 (só áudio)
ytdl-pro baixar "URL" --formato mp3

# Baixar playlist inteira
ytdl-pro playlist "https://youtube.com/playlist?list=XXXXXXXXX"

# Baixar vídeos 5 ao 20 de uma playlist
ytdl-pro playlist "URL" --inicio 5 --fim 20

# Ver histórico de downloads
ytdl-pro historico

# Ver configurações
ytdl-pro config --mostrar
```

---

## ESTRUTURA DOS ARQUIVOS BAIXADOS

```
~/Downloads/ytdl-pro/
├── Nome da Playlist/
│   ├── 01 - Título do Vídeo.mp4
│   ├── 01 - Título do Vídeo.pt.vtt   ← legenda português
│   ├── 01 - Título do Vídeo.jpg      ← thumbnail
│   ├── 02 - Segundo Vídeo.mp4
│   └── ...
└── Video Avulso.mp4

~/.config/ytdl-pro/
├── config.json     ← suas configurações
├── perfis.json     ← perfis de download
├── historico.json  ← histórico completo
└── .env            ← variáveis de ambiente
```

---

## CONFIGURAÇÃO VIA .ENV

Edite o arquivo `~/.config/ytdl-pro/.env`:
```env
YTDL_PASTA=D:\Videos          # pasta padrão (Windows)
YTDL_QUALIDADE=1080           # qualidade padrão
YTDL_THREADS=4                # downloads paralelos
YTDL_VELOCIDADE=5M            # limite de 5MB/s
YTDL_COOKIES=chrome           # cookies do Chrome
```

---

## VÍDEOS PRIVADOS / COM RESTRIÇÃO DE IDADE

No menu interativo → opção 6 (Cookies / Auth)
- Selecione seu navegador (Chrome, Firefox, Edge...)
- O ytdl-pro usa seus cookies automaticamente

---

## PERFIS DE DOWNLOAD

| Perfil     | Qualidade | Uso ideal           |
|------------|-----------|---------------------|
| Padrão     | 1080p     | Uso geral           |
| Econômico  | 480p      | Economizar espaço   |
| Ultra HD   | 4K        | Máxima qualidade    |
| Áudio      | MP3 320k  | Só música/podcasts  |

Crie perfis personalizados no menu → opção 4.

---

## SOLUÇÃO DE PROBLEMAS

### "ytdl-pro não reconhecido"
```bash
# Verifique se pip instalou corretamente
pip show ytdl-pro

# Se necessário, use diretamente
python -m ytdl_pro.main
```

### "ffmpeg não encontrado"
- Verifique se ffmpeg está no PATH: `ffmpeg -version`
- Reinstale seguindo o Passo 2

### Erro de qualidade (vídeo não disponível em 4K)
- O ytdl-pro escolhe automaticamente a melhor disponível
- Use o perfil "Econômico" para vídeos mais antigos

### Download lento
- Aumente os threads: menu → Configurações → Threads
- Configure no .env: `YTDL_THREADS=8`

### Cookie inválido / Vídeo restrito
- Abra o YouTube no navegador e faça login
- No menu → opção 6 → selecione seu navegador

---

## DEPENDÊNCIAS COMPLETAS

```
yt-dlp>=2024.1.0    → motor de download
rich>=13.0.0        → interface no terminal
python-dotenv       → arquivo .env
questionary         → menus interativos
click>=8.1.0        → comandos CLI
mutagen>=1.47.0     → metadados de áudio
requests>=2.31.0    → requisições HTTP
Pillow>=10.0.0      → processamento de imagens
ffmpeg              → conversão de vídeo/áudio
```
