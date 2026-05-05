"""
Motor principal de download — yt-dlp com suporte completo
"""

import os
import re
import time
import threading
from pathlib import Path
from typing import Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import yt_dlp

from config import ConfigManager, HistoricoManager
from ui import (
    console, exibir_sucesso, exibir_erro, exibir_aviso,
    exibir_info, criar_progresso_download, VERDE, LARANJA,
    VERMELHO, AMARELO, CIANO, CINZA, BRANCO, ROXO,
)
from rich.progress import Progress, TaskID
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box


class YTDLPro:
    """Motor de download ytdl-pro."""

    def __init__(self, config: ConfigManager, historico: HistoricoManager):
        self.config = config
        self.historico = historico
        self._lock = threading.Lock()
        self._stats = {
            "concluidos": 0,
            "erros": 0,
            "pulados": 0,
            "tamanho_bytes": 0,
            "inicio": datetime.now().strftime("%H:%M:%S"),
        }
        self._duplicata_resposta_global: Optional[str] = None

    # ── Opções do yt-dlp ─────────────────────────────────────────────────────

    def _construir_opcoes(
        self,
        pasta_destino: str,
        qualidade: str,
        formato: str = "mp4",
        numero_playlist: bool = True,
        progresso_callback: Optional[Callable] = None,
        cookiefile: Optional[str] = None,
    ) -> dict:

        # Formato de qualidade
        if qualidade == "audio" or formato in ("mp3", "flac", "wav", "m4a"):
            fmt_video = None
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": formato if formato in ("mp3", "flac", "wav", "m4a") else "mp3",
                    "preferredquality": "320" if formato == "mp3" else "0",
                }
            ]
        else:
            altura = qualidade if qualidade.isdigit() else "1080"
            fmt_video = (
                f"bestvideo[height<={altura}][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={altura}][vcodec^=avc]+bestaudio/"
                f"bestvideo[height<={altura}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={altura}]+bestaudio/best[height<={altura}]/best"
            )
            postprocessors = [
                {"key": "FFmpegVideoConvertor", "preferedformat": formato},
            ]

        # Thumbnails e metadados
        if self.config.get("thumbnails"):
            postprocessors += [
                {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
                {"key": "EmbedThumbnail"},
            ]
        if self.config.get("metadados"):
            postprocessors.append({"key": "FFmpegMetadata", "add_metadata": True})

        # Formato do nome do arquivo
        if numero_playlist:
            outtmpl = os.path.join(
                pasta_destino,
                "%(playlist_title)s" if self.config.get("subpasta_playlist") else "",
                "%(playlist_index)02d - %(title)s.%(ext)s",
            )
        else:
            outtmpl = os.path.join(pasta_destino, "%(title)s.%(ext)s")

        opcoes: dict = {
            "format": fmt_video or "bestaudio/best",
            "outtmpl": outtmpl,
            "merge_output_format": formato,
            "postprocessors": postprocessors,
            "writesubtitles": self.config.get("legendas", True),
            "writeautomaticsub": self.config.get("legendas", True),
            "subtitleslangs": ["pt", "pt-BR"] if self.config.get("legendas") else [],
            "writethumbnail": self.config.get("thumbnails", True),
            "addmetadata": self.config.get("metadados", True),
            "retries": self.config.get("max_retentativas", 3),
            "fragment_retries": self.config.get("max_retentativas", 3),
            "continuedl": self.config.get("retomar", True),  # retomar downloads
            "nooverwrites": False,
            "ignoreerrors": True,
            "no_color": True,
            "quiet": True,
            "no_warnings": False,
            "socket_timeout": self.config.get("timeout", 30),
            "concurrent_fragment_downloads": min(self.config.get("threads", 4), 8),
            "noprogress": progresso_callback is None,
        }

        # Cookies
        cookies_nav = self.config.get("cookies_navegador")
        cookies_arq = self.config.get("cookies_arquivo") or cookiefile
        if cookies_arq and Path(cookies_arq).exists():
            opcoes["cookiefile"] = cookies_arq
        elif cookies_nav:
            opcoes["cookiesfrombrowser"] = (cookies_nav,)

        # Proxy
        proxy = self.config.get("proxy")
        if proxy:
            opcoes["proxy"] = proxy

        # Limite de velocidade
        limite = self.config.get("limite_velocidade")
        if limite:
            opcoes["ratelimit"] = self._parse_velocidade(limite)

        # User-Agent
        ua = self.config.get("user_agent")
        if ua:
            opcoes["user_agent"] = ua

        # Callback de progresso
        if progresso_callback:
            opcoes["progress_hooks"] = [progresso_callback]

        return opcoes

    def _parse_velocidade(self, velocidade: str) -> Optional[int]:
        """Converte '5M' → 5242880 bytes/s."""
        if not velocidade:
            return None
        match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMG]?)$", velocidade.upper())
        if match:
            valor = float(match.group(1))
            unidade = match.group(2)
            mult = {"K": 1024, "M": 1024**2, "G": 1024**3}.get(unidade, 1)
            return int(valor * mult)
        return None

    # ── Busca de informações ─────────────────────────────────────────────────

    def buscar_info(self, url: str) -> Optional[dict]:
        """Busca metadados sem baixar."""
        opcoes = {
            "quiet": True,
            "no_color": True,
            "skip_download": True,
            "ignoreerrors": True,
        }
        cookies_nav = self.config.get("cookies_navegador")
        cookies_arq = self.config.get("cookies_arquivo")
        if cookies_arq and Path(cookies_arq).exists():
            opcoes["cookiefile"] = cookies_arq
        elif cookies_nav:
            opcoes["cookiesfrombrowser"] = (cookies_nav,)
        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            exibir_erro(f"Erro ao buscar informações: {e}")
            return None

    def buscar_formatos(self, url: str) -> list[dict]:
        """Lista formatos disponíveis."""
        info = self.buscar_info(url)
        if info:
            return info.get("formats", [])
        return []

    # ── Download único ───────────────────────────────────────────────────────

    def baixar_video(
        self,
        url: str,
        qualidade: Optional[str] = None,
        pasta_destino: Optional[str] = None,
        numero: int = 1,
        total: int = 1,
        info_pre: Optional[dict] = None,
    ) -> bool:
        """Baixa um único vídeo com painel de progresso completo."""

        qualidade = qualidade or self.config.get("qualidade_padrao", "1080")
        pasta = pasta_destino or self.config.get("pasta_destino", str(Path.home() / "Downloads" / "ytdl-pro"))
        formato = self.config.get("formato", "mp4")

        Path(pasta).mkdir(parents=True, exist_ok=True)

        # Verificar duplicata
        if info_pre:
            video_id = info_pre.get("id")
            if video_id:
                existente = self.historico.ja_baixado(video_id)
                if existente:
                    from ui import exibir_confirmacao_duplicata
                    resposta = self._duplicata_resposta_global
                    if not resposta:
                        titulo = info_pre.get("title", "Desconhecido")
                        caminho = existente.get("caminho", pasta)
                        resposta = exibir_confirmacao_duplicata(titulo, caminho)
                        if resposta == "T":
                            self._duplicata_resposta_global = "P"
                            resposta = "P"
                    if resposta == "P":
                        with self._lock:
                            self._stats["pulados"] += 1
                        return True
                    elif resposta == "S":
                        pass  # continua e sobrescreve
                    # "R" = renomear (yt-dlp trata automaticamente com autonumber)

        # Progresso
        progresso_atual = {"downloaded": 0, "total": 0, "velocidade": 0, "eta": 0, "status": ""}
        task_id: list[Optional[TaskID]] = [None]

        def hook_progresso(d: dict):
            if d["status"] == "downloading":
                progresso_atual["downloaded"] = d.get("downloaded_bytes", 0)
                progresso_atual["total"] = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                progresso_atual["velocidade"] = d.get("speed", 0) or 0
                progresso_atual["eta"] = d.get("eta", 0) or 0
                progresso_atual["status"] = "baixando"
            elif d["status"] == "finished":
                progresso_atual["status"] = "processando"

        opcoes = self._construir_opcoes(
            pasta_destino=pasta,
            qualidade=qualidade,
            formato=formato,
            numero_playlist=(total > 1),
            progresso_callback=hook_progresso,
        )

        titulo = (info_pre or {}).get("title", "Buscando...")
        canal = (info_pre or {}).get("uploader", "-")
        duracao_seg = (info_pre or {}).get("duration", 0)
        duracao = f"{duracao_seg // 60}:{duracao_seg % 60:02d}" if duracao_seg else "?"

        sucesso = False
        inicio = time.time()

        with criar_progresso_download() as prog:
            task = prog.add_task(
                description=titulo[:45] + ("…" if len(titulo) > 45 else ""),
                total=100,
                cor=VERDE,
                emoji="⬇",
            )

            def atualizar_progresso():
                while not sucesso and progresso_atual["status"] != "erro":
                    if progresso_atual["total"] > 0:
                        pct = (progresso_atual["downloaded"] / progresso_atual["total"]) * 100
                        prog.update(task, completed=min(pct, 99))
                    time.sleep(0.3)

            t = threading.Thread(target=atualizar_progresso, daemon=True)
            t.start()

            # Exibir painel de info acima da barra
            info_dict = {
                "titulo": titulo,
                "canal": canal,
                "duracao": duracao,
                "qualidade": f"{qualidade}p",
                "formato": formato,
            }
            self._exibir_painel_video(info_dict, numero, total)

            try:
                with yt_dlp.YoutubeDL(opcoes) as ydl:
                    cod = ydl.download([url])
                    sucesso = (cod == 0)
            except Exception as e:
                exibir_erro(f"Erro durante download: {e}")
                sucesso = False

            prog.update(task, completed=100)
            t.join(timeout=1)

        tempo = time.time() - inicio
        tamanho = progresso_atual.get("total", 0)

        # Registrar no histórico
        self.historico.adicionar({
            "video_id": (info_pre or {}).get("id"),
            "titulo": titulo,
            "canal": canal,
            "url": url,
            "qualidade": f"{qualidade}p",
            "formato": formato,
            "tamanho": self._formatar_tamanho(tamanho),
            "caminho": pasta,
            "tempo": f"{tempo:.1f}s",
            "status": "ok" if sucesso else "erro",
        })

        with self._lock:
            if sucesso:
                self._stats["concluidos"] += 1
                self._stats["tamanho_bytes"] += tamanho
                exibir_sucesso(f"Download concluído: {titulo[:50]}")
            else:
                self._stats["erros"] += 1
                exibir_erro(f"Falha no download: {titulo[:50]}")

        return sucesso

    # ── Download de playlist ──────────────────────────────────────────────────

    def baixar_playlist(
        self,
        url: str,
        qualidade: Optional[str] = None,
        pasta_destino: Optional[str] = None,
        inicio: int = 1,
        fim: Optional[int] = None,
    ) -> dict:
        """Baixa todos os vídeos de uma playlist."""

        qualidade = qualidade or self.config.get("qualidade_padrao", "1080")
        pasta = pasta_destino or self.config.get("pasta_destino", str(Path.home() / "Downloads" / "ytdl-pro"))
        formato = self.config.get("formato", "mp4")
        threads = self.config.get("threads", 4)

        self._duplicata_resposta_global = None

        # Busca info da playlist
        exibir_info("Buscando informações da playlist...")
        info_playlist = self.buscar_info(url)

        if not info_playlist:
            exibir_erro("Não foi possível obter informações da playlist.")
            return self._stats

        nome_playlist = info_playlist.get("title", "Playlist")
        entradas = info_playlist.get("entries", [])
        entradas = [e for e in entradas if e]  # filtrar None

        if not entradas:
            exibir_aviso("Nenhum vídeo encontrado na playlist.")
            return self._stats

        # Aplicar intervalo
        entradas = entradas[inicio - 1: fim]
        total = len(entradas)

        # Pasta da playlist
        nome_pasta = self._sanitizar_nome(nome_playlist)
        pasta_playlist = os.path.join(pasta, nome_pasta)
        Path(pasta_playlist).mkdir(parents=True, exist_ok=True)

        # Exibir resumo da playlist
        self._exibir_resumo_playlist(nome_playlist, total, qualidade, pasta_playlist)

        # Download paralelo ou sequencial
        if threads > 1:
            self._baixar_paralelo(entradas, qualidade, pasta_playlist, formato, threads)
        else:
            for i, entrada in enumerate(entradas, 1):
                url_video = entrada.get("webpage_url") or entrada.get("url")
                if url_video:
                    self.baixar_video(
                        url=url_video,
                        qualidade=qualidade,
                        pasta_destino=pasta_playlist,
                        numero=i,
                        total=total,
                        info_pre=entrada,
                    )

        return self._stats

    def _baixar_paralelo(
        self,
        entradas: list[dict],
        qualidade: str,
        pasta: str,
        formato: str,
        max_threads: int,
    ):
        """Download paralelo com ThreadPoolExecutor."""
        total = len(entradas)
        max_threads = min(max_threads, total, 8)

        exibir_info(f"Download paralelo com {max_threads} threads simultâneas")

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futuros = {}
            for i, entrada in enumerate(entradas, 1):
                url_video = entrada.get("webpage_url") or entrada.get("url")
                if url_video:
                    futuro = executor.submit(
                        self.baixar_video,
                        url=url_video,
                        qualidade=qualidade,
                        pasta_destino=pasta,
                        numero=i,
                        total=total,
                        info_pre=entrada,
                    )
                    futuros[futuro] = entrada.get("title", f"Vídeo {i}")

            for futuro in as_completed(futuros):
                titulo = futuros[futuro]
                try:
                    futuro.result()
                except Exception as e:
                    exibir_erro(f"Erro no thread para '{titulo}': {e}")
                    with self._lock:
                        self._stats["erros"] += 1

    # ── Utilitários ───────────────────────────────────────────────────────────

    def _exibir_painel_video(self, info: dict, numero: int, total: int):
        """Exibe painel de informações do vídeo atual."""
        grid = Table.grid(expand=False, padding=(0, 2))
        grid.add_column(style=f"bold {CIANO}", width=14)
        grid.add_column(style=BRANCO)

        from rich.markup import escape
        grid.add_row("🎬 Título:",    escape(info.get("titulo", "")[:55]))
        grid.add_row("📺 Canal:",     escape(info.get("canal", "-")))
        grid.add_row("⏱ Duração:",   info.get("duracao", "?"))
        grid.add_row("🎯 Qualidade:", f"[bold {VERDE}]{info.get('qualidade', '?')}[/]")
        grid.add_row("🔢 Vídeo:",     f"[bold {LARANJA}]{numero}[/] de [bold {LARANJA}]{total}[/]")

        console.print(Panel(
            grid,
            title=f"[bold {VERDE}]⬇  BAIXANDO  ⬇[/]",
            border_style=f"bold {VERDE}",
            padding=(0, 2),
        ))

    def _exibir_resumo_playlist(self, nome: str, total: int, qualidade: str, pasta: str):
        """Exibe resumo da playlist antes de iniciar."""
        from rich.markup import escape

        grid = Table.grid(expand=False, padding=(0, 2))
        grid.add_column(style=f"bold {CIANO}", width=16)
        grid.add_column(style=BRANCO)

        grid.add_row("📋 Playlist:", escape(nome[:55]))
        grid.add_row("📹 Total:",    f"[bold {AMARELO}]{total}[/] vídeos")
        grid.add_row("🎯 Qualidade:",f"[bold {VERDE}]{qualidade}p[/]")
        grid.add_row("📁 Pasta:",    escape(pasta[:55]))
        grid.add_row("⚡ Threads:",  str(self.config.get("threads", 4)))

        console.print(Panel(
            grid,
            title=f"[bold {AZUL}]📋  PLAYLIST DETECTADA  📋[/]",
            border_style=f"bold {AZUL}",
            padding=(1, 2),
        ))
        console.print()

    def _sanitizar_nome(self, nome: str) -> str:
        """Remove caracteres inválidos de nome de arquivo."""
        invalidos = r'<>:"/\|?*'
        for c in invalidos:
            nome = nome.replace(c, "_")
        return nome.strip()[:100]

    def _formatar_tamanho(self, bytes_: int) -> str:
        """Formata tamanho em bytes para string legível."""
        if not bytes_:
            return "?"
        for unidade in ("B", "KB", "MB", "GB"):
            if bytes_ < 1024:
                return f"{bytes_:.1f} {unidade}"
            bytes_ /= 1024
        return f"{bytes_:.1f} TB"

    def stats_sessao(self) -> dict:
        """Retorna estatísticas formatadas da sessão atual."""
        s = self._stats.copy()
        s["tamanho_total"] = self._formatar_tamanho(s.get("tamanho_bytes", 0))
        s["threads"] = self.config.get("threads", 4)
        s["pasta"] = self.config.get("pasta_destino", "-")
        return s

    def resetar_stats(self):
        self._stats = {
            "concluidos": 0,
            "erros": 0,
            "pulados": 0,
            "tamanho_bytes": 0,
            "inicio": datetime.now().strftime("%H:%M:%S"),
        }
        self._duplicata_resposta_global = None


# Importação atrasada para evitar circular
from ui import AZUL  # noqa
