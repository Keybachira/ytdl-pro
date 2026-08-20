import os
import json
from pathlib import Path

os.environ.setdefault("TERM", "xterm-256color")

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Button, DataTable, Input, ProgressBar, RichLog, Select, Static, Switch
from textual import work


# Configuração
CONFIG_DIR = Path.home() / ".config" / "ytdl-pro"
CONFIG_FILE = CONFIG_DIR / "config.json"

CONFIG_PADRAO = {
    "pasta_destino": str(Path.home() / "Downloads" / "ytdl-pro"),
    "qualidade_padrao": "1080",
}

PERFIS = {"Padrao": "Full HD", "Economico": "Menor tamanho"}


def carregar_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return {**CONFIG_PADRAO, **json.load(f)}
        except:
            pass
    return dict(CONFIG_PADRAO)


def salvar_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# Páginas
class PageDownload(Container):
    def compose(self):
        yield Static("▸ BAIXAR", classes="page-title")
        yield Static("URL:", classes="page-subtitle")
        yield Input(id="url-input")
        yield Select([("480p", "480"), ("720p", "720"), ("1080p", "1080")], value="1080", id="qualidade")
        yield Button("⬇ BAIXAR", id="btn-baixar")
        yield ProgressBar(id="progresso")
        yield RichLog(id="log")


class PageHistorico(Container):
    def compose(self):
        yield Static("▸ HISTORICO", classes="page-title")
        yield DataTable(id="tabela")


class PageConfig(ScrollableContainer):
    def compose(self):
        cfg = carregar_config()
        yield Static("▸ CONFIG", classes="page-title")
        yield Input(value=cfg.get("pasta_destino", ""), id="pasta")
        yield Select([("480p", "480"), ("720p", "720"), ("1080p", "1080")], value=cfg.get("qualidade_padrao", "1080"), id="qual")
        yield Button("SALVAR", id="btn-salvar")


class PagePerfis(Container):
    def compose(self):
        yield Static("▸ PERFIS", classes="page-title")
        for n, d in PERFIS.items():
            yield Static(f"• {n}: {d}")


class PageSobre(Container):
    def compose(self):
        yield Static("▸ YTDL-PRO v1.0.0", classes="page-title")


# App
class YTDLProApp(App):
    CSS_PATH = "styles/app.tcss"
    
    def compose(self):
        with Vertical(id="sidebar"):
            yield Static("MENU", classes="menu-label")
            yield Button("Baixar", id="nav-download")
            yield Button("Historico", id="nav-historico")
            yield Button("Config", id="nav-config")
            yield Button("Perfis", id="nav-perfis")
            yield Button("Sobre", id="nav-sobre")
        
        with Vertical(id="content"):
            yield PageDownload(id="page-download")
            yield PageHistorico(id="page-historico", classes="hidden")
            yield PageConfig(id="page-config", classes="hidden")
            yield PagePerfis(id="page-perfis", classes="hidden")
            yield PageSobre(id="page-sobre", classes="hidden")
    
    def on_button_pressed(self, event):
        bid = event.button.id or ""
        
        if bid.startswith("nav-"):
            self.mudar_pagina(bid[4:])
        elif bid == "btn-baixar":
            self.baixar()
        elif bid == "btn-salvar":
            self.salvar()
    
    def mudar_pagina(self, nome: str):
        for p in ["download", "historico", "config", "perfis", "sobre"]:
            w = self.query_one(f"#page-{p}")
            if p == nome:
                w.remove_class("hidden")
            else:
                w.add_class("hidden")
    
    def baixar(self):
        url = self.query_one("#url-input", Input).value.strip()
        if not url:
            self.notify("Cole uma URL!")
            return
        
        pasta = carregar_config().get("pasta_destino")
        Path(pasta).mkdir(parents=True, exist_ok=True)
        
        self.notify("Baixando...")
        
        import yt_dlp
        try:
            log = self.query_one("#log", RichLog)
            with yt_dlp.YoutubeDL({"outtmpl": str(Path(pasta) / "%(title)s.%(ext)s")}) as ydl:
                ydl.download([url])
            log.write("[green]Concluido![/green]")
        except Exception as e:
            self.notify(f"Erro: {e}")
    
    def salvar(self):
        cfg = carregar_config()
        cfg["pasta_destino"] = self.query_one("#pasta", Input).value
        cfg["qualidade_padrao"] = self.query_one("#qual", Select).value
        salvar_config(cfg)
        self.notify("Salvo!")


def main():
    YTDLProApp().run()


if __name__ == "__main__":
    main()