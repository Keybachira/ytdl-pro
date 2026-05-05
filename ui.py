"""
╔═══════════════════════════════════════════════════════════════╗
║                    YTDL-PRO  •  Interface TUI                 ║
║              Design visual com Rich + Animações               ║
╚═══════════════════════════════════════════════════════════════╝
"""

import time
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn,
    TimeRemainingColumn, TransferSpeedColumn, DownloadColumn,
    TaskProgressColumn, MofNCompleteColumn
)
from rich.live import Live
from rich.layout import Layout
from rich.padding import Padding
from rich import box
from rich.style import Style
from rich.markup import escape

console = Console()

# ── Paleta de cores ──────────────────────────────────────────────────────────
VERMELHO    = "#FF3B3B"
LARANJA     = "#FF6B35"
AMARELO     = "#FFD700"
VERDE       = "#00E676"
VERDE_ESC   = "#00BFA5"
AZUL        = "#2979FF"
ROXO        = "#7C4DFF"
CIANO       = "#00E5FF"
BRANCO      = "#F5F5F5"
CINZA       = "#757575"
CINZA_ESC   = "#212121"
FUNDO       = "#0D0D0D"


BANNER = r"""
 ██╗   ██╗████████╗██████╗ ██╗      ██████╗ ██████╗  ██████╗
 ╚██╗ ██╔╝╚══██╔══╝██╔══██╗██║     ██╔══██╗██╔══██╗██╔═══██╗
  ╚████╔╝    ██║   ██║  ██║██║     ██████╔╝██████╔╝██║   ██║
   ╚██╔╝     ██║   ██║  ██║██║     ██╔═══╝ ██╔══██╗██║   ██║
    ██║      ██║   ██████╔╝███████╗██║     ██║  ██║╚██████╔╝
    ╚═╝      ╚═╝   ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝
"""


def exibir_banner():
    """Exibe o banner principal animado."""
    console.clear()
    
    linhas = BANNER.strip().split('\n')
    cores = [VERMELHO, LARANJA, AMARELO, VERDE, AZUL, ROXO, CIANO]
    
    texto = Text()
    for i, linha in enumerate(linhas):
        cor = cores[i % len(cores)]
        texto.append(linha + "\n", style=f"bold {cor}")
    
    painel = Panel(
        Align.center(texto),
        border_style=f"bold {LARANJA}",
        padding=(0, 2),
    )
    console.print(painel)
    
    # Subtítulo
    sub = Text()
    sub.append("  ▶  ", style=f"bold {VERMELHO}")
    sub.append("Downloader Profissional de Vídeos e Playlists", style=f"bold {BRANCO}")
    sub.append("  ◀  ", style=f"bold {VERMELHO}")
    console.print(Align.center(sub))
    
    # Versão e info
    info = Text()
    info.append("  v1.0.0  ", style=f"dim {CINZA}")
    info.append("•", style=f"bold {LARANJA}")
    info.append("  Cross-Platform  ", style=f"dim {CINZA}")
    info.append("•", style=f"bold {LARANJA}")
    info.append("  YouTube + Playlists  ", style=f"dim {CINZA}")
    console.print(Align.center(info))
    console.print()


def exibir_menu_principal(perfis: list[str]) -> str:
    """Exibe o menu principal e retorna a opção escolhida."""
    opcoes = [
        ("1", "▶  Baixar Vídeo",          VERDE,    "Cole a URL de um vídeo do YouTube"),
        ("2", "📋  Baixar Playlist",       AZUL,     "Cole a URL de uma playlist completa"),
        ("3", "⚙️  Configurações",          AMARELO,  "Ajuste qualidade, pasta, threads e mais"),
        ("4", "👤  Gerenciar Perfis",       ROXO,     "Crie e edite perfis de download"),
        ("5", "📜  Histórico",              CIANO,    "Veja todos os downloads realizados"),
        ("6", "🍪  Cookies / Auth",         LARANJA,  "Configure cookies para vídeos privados"),
        ("7", "ℹ️  Sobre / Ajuda",          CINZA,    "Informações e comandos disponíveis"),
        ("0", "✖  Sair",                   VERMELHO, "Encerrar o programa"),
    ]
    
    tabela = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    tabela.add_column("Tecla", style=f"bold {AMARELO}", width=4)
    tabela.add_column("Opção", width=28)
    tabela.add_column("Descrição", style=f"dim {CINZA}")
    
    for tecla, nome, cor, desc in opcoes:
        tabela.add_row(
            f"[{tecla}]",
            Text(nome, style=f"bold {cor}"),
            desc,
        )
    
    # Perfil ativo
    perfil_txt = Text()
    perfil_txt.append("Perfil ativo: ", style=f"dim {CINZA}")
    perfil_txt.append(perfis[0] if perfis else "Padrão", style=f"bold {VERDE}")
    
    painel = Panel(
        tabela,
        title=f"[bold {LARANJA}]◈  MENU PRINCIPAL  ◈[/]",
        subtitle=perfil_txt,
        border_style=f"bold {ROXO}",
        padding=(1, 3),
    )
    
    console.print(Align.center(painel))
    console.print()
    
    escolha = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  [{BRANCO}]Digite a opção:[/{BRANCO}] "
    ).strip()
    return escolha


def criar_progresso_download() -> Progress:
    """Cria barra de progresso rica para download."""
    return Progress(
        SpinnerColumn(style=f"bold {LARANJA}"),
        TextColumn("[bold {task.fields[cor]}]{task.fields[emoji]} {task.description}"),
        BarColumn(
            bar_width=40,
            style=f"dim {AZUL}",
            complete_style=f"bold {VERDE}",
            finished_style=f"bold {VERDE_ESC}",
            pulse_style=f"bold {LARANJA}",
        ),
        TaskProgressColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )


def painel_download_video(
    titulo: str,
    canal: str,
    duracao: str,
    qualidade: str,
    formato: str,
    numero: int,
    total: int,
) -> Panel:
    """Cria painel de informações do vídeo sendo baixado."""
    
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(style=f"bold {CIANO}", width=14)
    grid.add_column(style=BRANCO)
    
    grid.add_row("🎬 Título:",    escape(titulo[:55]) + ("…" if len(titulo) > 55 else ""))
    grid.add_row("📺 Canal:",     escape(canal))
    grid.add_row("⏱ Duração:",   duracao)
    grid.add_row("🎯 Qualidade:", f"[bold {VERDE}]{qualidade}[/]")
    grid.add_row("📦 Formato:",   f"[bold {AMARELO}]{formato.upper()}[/]")
    grid.add_row("🔢 Progresso:", f"[bold {LARANJA}]{numero}[/] de [bold {LARANJA}]{total}[/]")
    
    return Panel(
        grid,
        title=f"[bold {VERDE}]⬇  BAIXANDO AGORA  ⬇[/]",
        border_style=f"bold {VERDE}",
        padding=(1, 2),
    )


def painel_estatisticas(stats: dict) -> Panel:
    """Painel lateral com estatísticas da sessão."""
    
    grid = Table.grid(padding=(0, 1))
    grid.add_column(style=f"dim {CINZA}", width=14)
    grid.add_column(style=f"bold {BRANCO}")
    
    grid.add_row("✅ Concluídos:", f"[bold {VERDE}]{stats.get('concluidos', 0)}[/]")
    grid.add_row("❌ Erros:",      f"[bold {VERMELHO}]{stats.get('erros', 0)}[/]")
    grid.add_row("⏭ Pulados:",    f"[bold {AMARELO}]{stats.get('pulados', 0)}[/]")
    grid.add_row("💾 Total:",      f"[bold {CIANO}]{stats.get('tamanho_total', '0 MB')}[/]")
    grid.add_row("⚡ Threads:",    f"[bold {ROXO}]{stats.get('threads', 1)}[/]")
    grid.add_row("🕐 Início:",     stats.get('inicio', '--:--'))
    
    return Panel(
        grid,
        title=f"[bold {CIANO}]📊 SESSÃO[/]",
        border_style=f"dim {AZUL}",
        padding=(1, 2),
    )


def exibir_layout_download(
    info_video: dict,
    stats: dict,
    progresso: Progress,
    numero: int,
    total: int,
):
    """Layout completo durante o download com Live."""
    layout = Layout()
    layout.split_column(
        Layout(name="info",  size=10),
        Layout(name="prog",  size=6),
        Layout(name="stats", size=10),
    )
    
    layout["info"].update(
        painel_download_video(
            titulo=info_video.get("titulo", "Desconhecido"),
            canal=info_video.get("canal", "Desconhecido"),
            duracao=info_video.get("duracao", "??:??"),
            qualidade=info_video.get("qualidade", "1080p"),
            formato=info_video.get("formato", "mp4"),
            numero=numero,
            total=total,
        )
    )
    layout["stats"].update(painel_estatisticas(stats))
    return layout


def exibir_confirmacao_duplicata(titulo: str, caminho: str) -> str:
    """Pergunta o que fazer com arquivo duplicado."""
    console.print()
    painel = Panel(
        Text.assemble(
            ("⚠  ARQUIVO JÁ EXISTE\n\n", f"bold {AMARELO}"),
            ("Título: ", f"bold {CINZA}"),
            (escape(titulo) + "\n", BRANCO),
            ("Local:  ", f"bold {CINZA}"),
            (escape(caminho) + "\n\n", f"dim {CINZA}"),
            ("O que deseja fazer?", f"bold {BRANCO}"),
        ),
        border_style=f"bold {AMARELO}",
        padding=(1, 3),
    )
    console.print(Align.center(painel))
    
    opcoes = Table(show_header=False, box=box.SIMPLE, padding=(0, 3))
    opcoes.add_column("Tecla", style=f"bold {AMARELO}")
    opcoes.add_column("Ação")
    opcoes.add_row("[S]", Text("Substituir arquivo existente", style=f"bold {VERMELHO}"))
    opcoes.add_row("[P]", Text("Pular este vídeo",            style=f"bold {CINZA}"))
    opcoes.add_row("[R]", Text("Renomear (adicionar sufixo)", style=f"bold {VERDE}"))
    opcoes.add_row("[T]", Text("Aplicar a todos os próximos", style=f"bold {ROXO}"))
    console.print(Align.center(opcoes))
    
    escolha = console.input(
        f"\n  [{AMARELO}]➤[/{AMARELO}]  Escolha [S/P/R/T]: "
    ).strip().upper()
    return escolha if escolha in ("S", "P", "R", "T") else "P"


def exibir_tabela_historico(registros: list[dict]):
    """Exibe tabela completa do histórico de downloads."""
    console.clear()
    exibir_cabecalho("📜  HISTÓRICO DE DOWNLOADS")
    
    if not registros:
        console.print(Align.center(
            Panel(
                Text("Nenhum download registrado ainda.", style=f"dim {CINZA}"),
                border_style=f"dim {CINZA}",
                padding=(2, 6),
            )
        ))
        return
    
    tabela = Table(
        title=f"[bold {AMARELO}]Total: {len(registros)} downloads[/]",
        box=box.ROUNDED,
        border_style=f"dim {ROXO}",
        header_style=f"bold {LARANJA}",
        show_lines=True,
        expand=True,
    )
    
    tabela.add_column("#",        style=f"bold {AMARELO}", width=4,  justify="right")
    tabela.add_column("Título",   style=BRANCO,            width=35, no_wrap=True)
    tabela.add_column("Canal",    style=f"dim {CIANO}",    width=18, no_wrap=True)
    tabela.add_column("Qualidade",style=f"bold {VERDE}",   width=10, justify="center")
    tabela.add_column("Formato",  style=f"bold {AMARELO}", width=8,  justify="center")
    tabela.add_column("Tamanho",  style=AZUL,              width=10, justify="right")
    tabela.add_column("Data",     style=f"dim {CINZA}",    width=16)
    tabela.add_column("Status",   width=10, justify="center")
    
    for i, reg in enumerate(reversed(registros[-100:]), 1):
        status_emoji = "✅" if reg.get("status") == "ok" else "❌"
        status_style = VERDE if reg.get("status") == "ok" else VERMELHO
        
        tabela.add_row(
            str(i),
            escape(reg.get("titulo", "")[:34]),
            escape(reg.get("canal", "")[:17]),
            reg.get("qualidade", "-"),
            reg.get("formato", "-").upper(),
            reg.get("tamanho", "-"),
            reg.get("data", "-"),
            Text(status_emoji, style=f"bold {status_style}"),
        )
    
    console.print(tabela)


def exibir_cabecalho(titulo: str):
    """Cabeçalho de seção."""
    console.print()
    console.print(Rule(
        f"[bold {LARANJA}]{titulo}[/]",
        style=f"dim {ROXO}",
    ))
    console.print()


def exibir_sucesso(mensagem: str):
    """Mensagem de sucesso."""
    console.print(Panel(
        Text(f"✅  {mensagem}", style=f"bold {VERDE}"),
        border_style=f"bold {VERDE}",
        padding=(0, 2),
    ))


def exibir_erro(mensagem: str):
    """Mensagem de erro."""
    console.print(Panel(
        Text(f"❌  {mensagem}", style=f"bold {VERMELHO}"),
        border_style=f"bold {VERMELHO}",
        padding=(0, 2),
    ))


def exibir_aviso(mensagem: str):
    """Mensagem de aviso."""
    console.print(Panel(
        Text(f"⚠  {mensagem}", style=f"bold {AMARELO}"),
        border_style=f"bold {AMARELO}",
        padding=(0, 2),
    ))


def exibir_info(mensagem: str):
    """Mensagem informativa."""
    console.print(f"  [{CIANO}]ℹ[/{CIANO}]  {mensagem}")


def spinner_buscando(url: str):
    """Spinner enquanto busca informações do vídeo."""
    return console.status(
        f"[bold {LARANJA}]🔍 Buscando informações...[/]  [dim]{escape(url[:60])}[/]",
        spinner="dots",
        spinner_style=f"bold {LARANJA}",
    )


def exibir_info_video(info: dict):
    """Painel com informações do vídeo antes de baixar."""
    
    grid = Table.grid(expand=False, padding=(0, 2))
    grid.add_column(style=f"bold {CIANO}", width=14)
    grid.add_column(style=BRANCO, max_width=60)
    
    titulo = info.get("title", "Desconhecido")
    canal = info.get("uploader", "Desconhecido")
    duracao_seg = info.get("duration", 0)
    duracao = f"{duracao_seg // 60}:{duracao_seg % 60:02d}" if duracao_seg else "Ao vivo"
    views = f"{info.get('view_count', 0):,}".replace(",", ".")
    data_pub = info.get("upload_date", "")
    if data_pub and len(data_pub) == 8:
        data_pub = f"{data_pub[6:8]}/{data_pub[4:6]}/{data_pub[:4]}"
    
    grid.add_row("🎬 Título:",    escape(titulo))
    grid.add_row("📺 Canal:",     escape(canal))
    grid.add_row("⏱ Duração:",   duracao)
    grid.add_row("👁 Views:",     views)
    grid.add_row("📅 Publicado:", data_pub or "Desconhecido")
    grid.add_row("🔗 ID:",        info.get("id", "-"))
    
    console.print(Panel(
        grid,
        title=f"[bold {AZUL}]📹  INFORMAÇÕES DO VÍDEO[/]",
        border_style=f"bold {AZUL}",
        padding=(1, 2),
    ))
    console.print()


def exibir_selecao_qualidade(formatos_disponiveis: list[dict]) -> str:
    """Menu interativo de seleção de qualidade."""
    
    perfis = [
        ("1", "🟢  Econômico",  "480p",  "Menor arquivo, qualidade boa"),
        ("2", "🔵  Padrão",     "720p",  "Equilíbrio entre qualidade e tamanho"),
        ("3", "🟠  Alta",       "1080p", "Full HD - recomendado"),
        ("4", "🔴  Ultra",      "1440p", "2K - alto consumo de espaço"),
        ("5", "⭐  Máxima",     "4K",    "Melhor disponível (pode ser 4K)"),
        ("6", "🎛  Personalizar","Custom","Escolher resolução exata"),
    ]
    
    tabela = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    tabela.add_column("Tecla", style=f"bold {AMARELO}", width=4)
    tabela.add_column("Perfil", width=20)
    tabela.add_column("Res.", style=f"bold {VERDE}", width=8)
    tabela.add_column("Descrição", style=f"dim {CINZA}")
    
    for tecla, nome, res, desc in perfis:
        tabela.add_row(f"[{tecla}]", Text(nome, style=f"bold {BRANCO}"), res, desc)
    
    console.print(Panel(
        tabela,
        title=f"[bold {AMARELO}]🎯  SELECIONE A QUALIDADE[/]",
        border_style=f"bold {AMARELO}",
        padding=(1, 2),
    ))
    
    escolha = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  Opção [1-6]: "
    ).strip()
    
    mapa = {"1": "480", "2": "720", "3": "1080", "4": "1440", "5": "2160"}
    
    if escolha == "6":
        # Mostra formatos disponíveis
        console.print()
        fmt_tabela = Table(
            show_header=True, box=box.SIMPLE_HEAD,
            header_style=f"bold {LARANJA}",
        )
        fmt_tabela.add_column("ID",         style=f"bold {AMARELO}", width=10)
        fmt_tabela.add_column("Resolução",  style=f"bold {VERDE}",   width=12)
        fmt_tabela.add_column("Codec",      style=BRANCO,            width=10)
        fmt_tabela.add_column("Ext.",       style=f"bold {CIANO}",   width=6)
        fmt_tabela.add_column("Tamanho",    style=AZUL,              width=12)
        
        for fmt in formatos_disponiveis[:15]:
            if fmt.get("vcodec") and fmt.get("vcodec") != "none":
                height = fmt.get("height") or 0
                tam = fmt.get("filesize")
                tam_str = f"{tam / 1024 / 1024:.1f} MB" if tam else "?"
                fmt_tabela.add_row(
                    fmt.get("format_id", "-"),
                    f"{height}p" if height else "-",
                    (fmt.get("vcodec") or "-")[:10],
                    fmt.get("ext", "-"),
                    tam_str,
                )
        
        console.print(fmt_tabela)
        formato_id = console.input(
            f"\n  [{AMARELO}]➤[/{AMARELO}]  Digite o ID do formato: "
        ).strip()
        return formato_id
    
    return mapa.get(escolha, "1080")


def exibir_resumo_final(stats: dict):
    """Exibe resumo final da sessão de download."""
    console.print()
    
    grid = Table.grid(expand=False, padding=(0, 3))
    grid.add_column(style=f"bold {CINZA}", width=18)
    grid.add_column(style=f"bold {BRANCO}")
    
    grid.add_row("✅ Concluídos:",   f"[bold {VERDE}]{stats.get('concluidos', 0)}[/] vídeos")
    grid.add_row("❌ Erros:",        f"[bold {VERMELHO}]{stats.get('erros', 0)}[/] vídeos")
    grid.add_row("⏭  Pulados:",      f"[bold {AMARELO}]{stats.get('pulados', 0)}[/] vídeos")
    grid.add_row("💾 Total baixado:", f"[bold {CIANO}]{stats.get('tamanho_total', '0 MB')}[/]")
    grid.add_row("⏱ Tempo total:",   stats.get("tempo_total", "0s"))
    grid.add_row("📁 Pasta:",        escape(stats.get("pasta", "-")))
    
    cor_borda = VERDE if stats.get("erros", 0) == 0 else AMARELO
    
    console.print(Panel(
        Align.center(grid),
        title=f"[bold {VERDE}]🏁  DOWNLOAD CONCLUÍDO  🏁[/]",
        border_style=f"bold {cor_borda}",
        padding=(1, 4),
    ))
    console.print()


def exibir_tela_configuracoes(config: dict) -> dict:
    """Tela de configurações interativa."""
    exibir_cabecalho("⚙️  CONFIGURAÇÕES")
    
    opcoes = [
        ("1", "📁  Pasta de destino",      str(config.get("pasta_destino", "~/Downloads/ytdl-pro"))),
        ("2", "🎯  Qualidade padrão",       config.get("qualidade_padrao", "1080")),
        ("3", "⚡  Threads de download",    str(config.get("threads", 4))),
        ("4", "🔤  Formato do arquivo",     config.get("formato_nome", "01 - Titulo.mp4")),
        ("5", "🌐  Proxy",                  config.get("proxy", "Nenhum")),
        ("6", "📝  Legendas",               "Ativadas (PT)" if config.get("legendas") else "Desativadas"),
        ("7", "🖼  Thumbnails",             "Embutidas + Arquivo" if config.get("thumbnails") else "Desativadas"),
        ("8", "🔄  Retomar downloads",      "Sim" if config.get("retomar") else "Não"),
        ("9", "🔒  Limite de velocidade",   config.get("limite_velocidade", "Ilimitado")),
        ("S", "💾  Salvar e voltar",        ""),
        ("C", "❌  Cancelar",               ""),
    ]
    
    tabela = Table(show_header=False, box=box.SIMPLE, padding=(0, 2), expand=True)
    tabela.add_column("Tecla", style=f"bold {AMARELO}", width=4)
    tabela.add_column("Configuração", width=26)
    tabela.add_column("Valor atual", style=f"bold {VERDE}")
    
    for tecla, nome, valor in opcoes:
        estilo_nome = f"bold {BRANCO}" if tecla not in ("S", "C") else (
            f"bold {VERDE}" if tecla == "S" else f"bold {VERMELHO}"
        )
        tabela.add_row(f"[{tecla}]", Text(nome, style=estilo_nome), valor)
    
    console.print(Panel(
        tabela,
        title=f"[bold {AMARELO}]⚙  AJUSTES DO SISTEMA[/]",
        border_style=f"bold {AMARELO}",
        padding=(1, 2),
    ))
    
    escolha = console.input(
        f"\n  [{AMARELO}]➤[/{AMARELO}]  Selecione o que ajustar: "
    ).strip().upper()
    
    return {"acao": escolha, "config": config}


def exibir_tela_perfis(perfis: dict) -> dict:
    """Tela de gerenciamento de perfis."""
    exibir_cabecalho("👤  GERENCIAR PERFIS")
    
    tabela = Table(
        box=box.ROUNDED,
        border_style=f"dim {ROXO}",
        header_style=f"bold {LARANJA}",
        show_lines=True,
    )
    tabela.add_column("#",          style=f"bold {AMARELO}", width=4,  justify="right")
    tabela.add_column("Nome",       style=f"bold {BRANCO}",  width=20)
    tabela.add_column("Qualidade",  style=f"bold {VERDE}",   width=10, justify="center")
    tabela.add_column("Formato",    style=f"bold {CIANO}",   width=8,  justify="center")
    tabela.add_column("Threads",    style=AZUL,              width=8,  justify="center")
    tabela.add_column("Pasta",      style=f"dim {CINZA}",    width=30)
    
    for i, (nome, p) in enumerate(perfis.items(), 1):
        tabela.add_row(
            str(i),
            nome,
            p.get("qualidade", "1080"),
            p.get("formato", "mp4").upper(),
            str(p.get("threads", 4)),
            p.get("pasta_destino", "~/Downloads/ytdl-pro"),
        )
    
    console.print(tabela)
    console.print()
    
    acoes = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    acoes.add_column("Tecla", style=f"bold {AMARELO}", width=4)
    acoes.add_column("Ação")
    acoes.add_row("[N]", Text("Novo perfil",         style=f"bold {VERDE}"))
    acoes.add_row("[E]", Text("Editar perfil",        style=f"bold {AZUL}"))
    acoes.add_row("[D]", Text("Deletar perfil",       style=f"bold {VERMELHO}"))
    acoes.add_row("[A]", Text("Ativar perfil",        style=f"bold {CIANO}"))
    acoes.add_row("[V]", Text("Voltar",               style=f"dim {CINZA}"))
    console.print(acoes)
    
    return console.input(
        f"\n  [{AMARELO}]➤[/{AMARELO}]  Ação [N/E/D/A/V]: "
    ).strip().upper()


def exibir_sobre():
    """Tela sobre o software."""
    exibir_cabecalho("ℹ️  SOBRE O YTDL-PRO")
    
    texto = Text()
    texto.append("  YTDL-PRO v1.0.0\n", style=f"bold {LARANJA}")
    texto.append("  ─────────────────────────────────────────\n\n", style=f"dim {CINZA}")
    texto.append("  Downloader profissional para YouTube.\n", style=BRANCO)
    texto.append("  Construído com Python + yt-dlp + Rich.\n\n", style=f"dim {CINZA}")
    texto.append("  COMANDOS RÁPIDOS:\n", style=f"bold {AMARELO}")
    texto.append("  ytdl-pro              ", style=f"bold {VERDE}")
    texto.append("→ Abre o menu interativo\n", style=CINZA)
    texto.append("  ytdl-pro baixar URL   ", style=f"bold {VERDE}")
    texto.append("→ Baixa um vídeo direto\n", style=CINZA)
    texto.append("  ytdl-pro playlist URL ", style=f"bold {VERDE}")
    texto.append("→ Baixa playlist\n", style=CINZA)
    texto.append("  ytdl-pro historico    ", style=f"bold {VERDE}")
    texto.append("→ Ver histórico\n\n", style=CINZA)
    texto.append("  DEPENDÊNCIAS:\n", style=f"bold {AMARELO}")
    texto.append("  • yt-dlp  • rich  • ffmpeg  • mutagen\n", style=f"dim {CINZA}")
    texto.append("  • questionary  • click  • python-dotenv\n\n", style=f"dim {CINZA}")
    texto.append("  ⚠  Respeite os direitos autorais.\n", style=f"bold {AMARELO}")
    texto.append("  Use apenas para conteúdo que você\n", style=f"dim {CINZA}")
    texto.append("  tem permissão de baixar.\n", style=f"dim {CINZA}")
    
    console.print(Panel(
        texto,
        border_style=f"bold {ROXO}",
        padding=(1, 2),
    ))
    
    console.input(f"\n  [{CINZA}]Pressione ENTER para voltar...[/]")
