from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Static, Button, Input, Label, ProgressBar, RichLog, Select, DataTable
from textual.binding import Binding

from pathlib import Path

from config import ConfigManager, HistoricoManager
from downloader import YTDLPro


def main():
    YTDLProApp().run()


class YTDLProApp(App):
    CSS_PATH = "styles/app.tcss"
    TITLE = "YTDL-PRO"
    
    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("d", "toggle_dark", "Tema"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.historico = HistoricoManager()
        self.motor = YTDLPro(self.config, self.historico)
        self.tela_atual = "baixar"
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                yield Static("◈ YTDL-PRO", classes="sidebar-titulo")
                yield Static("v1.0.0", classes="sidebar-version")
                yield Static("", classes="sidebar-divider")
                
                yield Button("▶ Baixar Vídeo", id="btn-video", classes="sidebar-btn")
                yield Button("📋 Playlist", id="btn-playlist", classes="sidebar-btn")
                yield Button("📜 Histórico", id="btn-historico", classes="sidebar-btn")
                yield Button("⚙ Configurações", id="btn-config", classes="sidebar-btn")
                yield Button("👤 Perfis", id="btn-perfis", classes="sidebar-btn")
                yield Button("🍪 Cookies", id="btn-cookies", classes="sidebar-btn")
                yield Button("ℹ Sobre", id="btn-sobre", classes="sidebar-btn")
                
                yield Static("", classes="sidebar-spacer")
                yield Static("─" * 14, classes="sidebar-divider")
                yield Button("0 Sair", id="btn-sair", classes="sidebar-btn sidebar-sair")
            
            with Vertical(id="content"):
                self._render_tela_conteudo("baixar")
        
        yield Footer()
    
    def _render_tela_conteudo(self, nome: str):
        """Rederiza o conteúdo de uma tela."""
        
        if nome == "baixar":
            return self._tela_baixar()
        elif nome == "playlist":
            return self._tela_playlist()
        elif nome == "historico":
            return self._tela_historico()
        elif nome == "config":
            return self._tela_config()
        elif nome == "perfis":
            return self._tela_perfis()
        elif nome == "cookies":
            return self._tela_cookies()
        elif nome == "sobre":
            return self._tela_sobre()
        return self._tela_baixar()
    
    def _tela_baixar(self):
        yield Static("▶ BAIXAR VÍDEO", classes="content-titulo")
        yield Static("", classes="content-spacer")
        yield Static("Cole a URL do vídeo ou playlist:", classes="content-label")
        yield Input(placeholder="https://youtube.com/watch?v=...", id="url-input")
        yield Static("", classes="content-spacer")
        yield Static("Qualidade:", classes="content-label")
        yield Select([("480p", "480"), ("720p", "720"), ("1080p", "1080"), ("1440p", "1440")], value="1080", id="qualidade")
        yield Static("", classes="content-spacer")
        yield Button("⬇ BAIXAR AGORA", id="btn-download", classes="btn-download")
        yield Static("", classes="content-spacer")
        yield ProgressBar(id="progresso")
        yield RichLog(id="log", classes="log-area")
    
    def _tela_playlist(self):
        yield Static("📋 BAIXAR PLAYLIST", classes="content-titulo")
        yield Static("", classes="content-spacer")
        yield Static("Cole a URL da playlist:", classes="content-label")
        yield Input(placeholder="https://youtube.com/playlist?list=...", id="url-playlist")
        yield Static("", classes="content-spacer")
        yield Static("Qualidade:", classes="content-label")
        yield Select([("480p", "480"), ("720p", "720"), ("1080p", "1080")], value="1080", id="qualidade-pl")
        yield Static("", classes="content-spacer")
        yield Button("📋 BAIXAR PLAYLIST", id="btn-dl-playlist", classes="btn-download")
        yield Static("", classes="content-spacer")
        yield RichLog(id="log-pl", classes="log-area")
    
    def _tela_historico(self):
        yield Static("📜 HISTÓRICO", classes="content-titulo")
        yield Static("", classes="content-spacer")
        
        regs = self.historico.todos()
        if not regs:
            yield Static("Nenhum download ainda.", classes="content-label")
        else:
            yield Static(f"Total: {len(regs)} downloads", classes="content-label")
            yield Static("", classes="content-spacer")
            for r in regs[-10:]:
                titulo = r.get("title", "?")[:35]
                status = "✓" if r.get("status") == "sucesso" else "✗"
                yield Static(f"{status} {titulo}", classes="config-item")
    
    def _tela_config(self):
        yield Static("⚙ CONFIGURAÇÕES", classes="content-titulo")
        yield Static("", classes="content-spacer")
        
        pasta = self.config.get("pasta_destino", str(Path.home() / "Downloads" / "ytdl-pro"))
        yield Static(f"Pasta: {pasta[:40]}...", classes="config-item")
        yield Static(f"Threads: {self.config.get('threads', '4')}", classes="config-item")
        yield Static(f"Qualidade: {self.config.get('qualidade_padrao', '1080')}p", classes="config-item")
    
    def _tela_perfis(self):
        yield Static("👤 PERFIS", classes="content-titulo")
        yield Static("", classes="content-spacer")
        nomes = self.config.nomes_perfis()
        for n in nomes:
            yield Static(f"• {n}", classes="config-item")
    
    def _tela_cookies(self):
        yield Static("🍪 COOKIES", classes="content-titulo")
        yield Static("", classes="content-spacer")
        yield Static("Para vídeos privados:", classes="content-label")
        yield Button("📂 CARREGAR", id="btn-cookies", classes="btn-download")
    
    def _tela_sobre(self):
        yield Static("ℹ SOBRE", classes="content-titulo")
        yield Static("", classes="content-spacer")
        yield Static("YTDL-PRO v1.0.0", classes="content-titulo")
        yield Static("Downloader de vídeos YouTube", classes="content-label")
        yield Static("", classes="content-spacer")
        yield Static("Recursos:", classes="content-titulo")
        yield Static("• Vídeos e playlists", classes="config-item")
        yield Static("• Qualidades até 4K", classes="config-item")
        yield Static("• MP3 e legendas", classes="config-item")
    
    def on_mount(self) -> None:
        self._atualizar_botoes("baixar")
    
    def _atualizar_botoes(self, nome: str):
        for btn in self.query(".sidebar-btn"):
            btn.remove_class("selected")
        try:
            self.query_one(f"#{'btn-' + nome}", Button).add_class("selected")
        except:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        
        mapas = {
            "btn-video": "baixar",
            "btn-playlist": "playlist",
            "btn-historico": "historico",
            "btn-config": "config",
            "btn-perfis": "perfis",
            "btn-cookies": "cookies",
            "btn-sobre": "sobre",
            "btn-sair": "sair",
        }
        
        if btn_id == "btn-download":
            self._baixar()
        elif btn_id == "btn-sair":
            self.exit()
        elif btn_id in mapas:
            self._trocar_tela(mapas[btn_id])
    
    def _trocar_tela(self, nome: str):
        """Troca a tela atual."""
        self.tela_atual = nome
        
        content = self.query_one("#content", Vertical)
        content.remove_children()
        
        for w in self._render_tela_conteudo(nome):
            content.mount(w)
        
        self._atualizar_botoes(nome)
    
    def _baixar(self):
        url = self.query_one("#url-input", Input).value.strip()
        log = self.query_one("#log", RichLog)
        
        if not url:
            log.write("[red]Cole uma URL![/red]")
            return
        
        log.write(f"[cyan]↻ {url}[/cyan]")
        
        try:
            info = self.motor.buscar_info(url)
            if info:
                titulo = info.get("title", "?")
                log.write(f"[green]✓ {titulo}[/green]")
                
                pasta = self.config.get("pasta_destino", str(Path.home() / "Downloads" / "ytdl-pro"))
                qual = self.query_one("#qualidade", Select).value
                
                self.motor.baixar_video(url=url, qualidade=qual, pasta_destino=pasta, numero=1, total=1, info_pre=info)
                log.write("[bold green]✓ OK![/bold green]")
            else:
                log.write("[red]Erro![/red]")
        except Exception as e:
            log.write(f"[red]{e}[/red]")


if __name__ == "__main__":
    main()