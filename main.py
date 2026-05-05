"""
YTDL-PRO — Ponto de entrada principal
Interface híbrida: menu TUI + progresso animado
"""

import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .config import ConfigManager, HistoricoManager
from .downloader import YTDLPro
from .ui import (
    console,
    exibir_banner,
    exibir_menu_principal,
    exibir_cabecalho,
    exibir_sucesso,
    exibir_erro,
    exibir_aviso,
    exibir_info,
    exibir_tabela_historico,
    exibir_tela_configuracoes,
    exibir_tela_perfis,
    exibir_sobre,
    exibir_resumo_final,
    exibir_info_video,
    exibir_selecao_qualidade,
    spinner_buscando,
    AMARELO, VERDE, VERMELHO, CIANO, CINZA, BRANCO, LARANJA, ROXO,
)


# ── Verificação de dependências ───────────────────────────────────────────────

def verificar_ffmpeg() -> bool:
    import shutil
    return shutil.which("ffmpeg") is not None


def verificar_dependencias():
    """Verifica se ffmpeg está instalado."""
    if not verificar_ffmpeg():
        exibir_aviso(
            "FFmpeg não encontrado! Algumas funções podem não funcionar.\n"
            "  Instale em: https://ffmpeg.org/download.html\n"
            "  Linux: sudo apt install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Windows: https://www.gyan.dev/ffmpeg/builds/"
        )


# ── Fluxos de interação ───────────────────────────────────────────────────────

def fluxo_baixar_video(motor: YTDLPro, config: ConfigManager):
    """Fluxo interativo para baixar um único vídeo."""
    exibir_cabecalho("▶  BAIXAR VÍDEO")

    url = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  Cole a URL do vídeo: "
    ).strip()

    if not url:
        exibir_aviso("Nenhuma URL fornecida.")
        return

    # Buscar informações
    with spinner_buscando(url):
        info = motor.buscar_info(url)

    if not info:
        exibir_erro("Não foi possível obter informações do vídeo.")
        return

    # Verificar se é playlist
    if info.get("_type") == "playlist" or info.get("entries"):
        exibir_aviso("Esta URL é uma playlist! Redirecionando para o modo playlist...")
        time.sleep(1)
        fluxo_baixar_playlist(motor, config, url_pre=url, info_pre=info)
        return

    # Exibir info do vídeo
    exibir_info_video(info)

    # Selecionar qualidade
    formatos = info.get("formats", [])
    qualidade = exibir_selecao_qualidade(formatos)

    # Confirmar pasta
    pasta_atual = config.get("pasta_destino", str(Path.home() / "Downloads" / "ytdl-pro"))
    console.print(f"  [{CINZA}]Pasta de destino:[/] [{VERDE}]{pasta_atual}[/]")
    mudar = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  Manter esta pasta? [S/n]: "
    ).strip().lower()

    if mudar == "n":
        nova_pasta = console.input(
            f"  [{AMARELO}]➤[/{AMARELO}]  Nova pasta: "
        ).strip()
        if nova_pasta:
            pasta_atual = nova_pasta

    console.print()
    inicio = time.time()
    motor.resetar_stats()

    sucesso = motor.baixar_video(
        url=url,
        qualidade=qualidade,
        pasta_destino=pasta_atual,
        numero=1,
        total=1,
        info_pre=info,
    )

    tempo_total = time.time() - inicio
    stats = motor.stats_sessao()
    stats["tempo_total"] = f"{tempo_total:.1f}s"
    stats["pasta"] = pasta_atual
    exibir_resumo_final(stats)

    console.input(f"\n  [{CINZA}]Pressione ENTER para continuar...[/]")


def fluxo_baixar_playlist(
    motor: YTDLPro,
    config: ConfigManager,
    url_pre: Optional[str] = None,
    info_pre: Optional[dict] = None,
):
    """Fluxo interativo para baixar uma playlist."""
    exibir_cabecalho("📋  BAIXAR PLAYLIST")

    if url_pre:
        url = url_pre
    else:
        url = console.input(
            f"  [{AMARELO}]➤[/{AMARELO}]  Cole a URL da playlist: "
        ).strip()

    if not url:
        exibir_aviso("Nenhuma URL fornecida.")
        return

    # Buscar informações da playlist
    if not info_pre:
        with spinner_buscando(url):
            info_pre = motor.buscar_info(url)

    if not info_pre:
        exibir_erro("Não foi possível obter informações da playlist.")
        return

    entradas = info_pre.get("entries", [])
    total_original = len([e for e in entradas if e])
    nome = info_pre.get("title", "Playlist")

    console.print(f"\n  [{CIANO}]📋 Playlist:[/] [{BRANCO}]{nome}[/]")
    console.print(f"  [{CIANO}]📹 Total:[/]    [{AMARELO}]{total_original}[/] vídeos\n")

    # Selecionar qualidade
    qualidade = exibir_selecao_qualidade([])

    # Pasta destino
    pasta_atual = config.get("pasta_destino", str(Path.home() / "Downloads" / "ytdl-pro"))
    console.print(f"\n  [{CINZA}]Pasta base:[/] [{VERDE}]{pasta_atual}[/]")
    console.print(f"  [{CINZA}]Será criada subpasta:[/] [{VERDE}]{pasta_atual}/{nome[:40]}[/]\n")

    mudar = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  Manter pasta? [S/n]: "
    ).strip().lower()
    if mudar == "n":
        nova_pasta = console.input(
            f"  [{AMARELO}]➤[/{AMARELO}]  Nova pasta base: "
        ).strip()
        if nova_pasta:
            pasta_atual = nova_pasta

    # Confirmar início
    console.print()
    confirmar = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  Iniciar download de [{AMARELO}]{total_original}[/] vídeos? [S/n]: "
    ).strip().lower()

    if confirmar == "n":
        exibir_aviso("Download cancelado pelo usuário.")
        return

    inicio = time.time()
    motor.resetar_stats()
    motor.baixar_playlist(
        url=url,
        qualidade=qualidade,
        pasta_destino=pasta_atual,
    )

    tempo_total = time.time() - inicio
    stats = motor.stats_sessao()
    stats["tempo_total"] = f"{tempo_total:.1f}s"
    stats["pasta"] = pasta_atual
    exibir_resumo_final(stats)

    console.input(f"\n  [{CINZA}]Pressione ENTER para continuar...[/]")


def fluxo_configuracoes(config: ConfigManager):
    """Fluxo de configurações."""
    while True:
        resultado = exibir_tela_configuracoes(config.config)
        acao = resultado["acao"]

        if acao == "S":
            config.salvar()
            exibir_sucesso("Configurações salvas com sucesso!")
            time.sleep(1)
            break
        elif acao == "C":
            break
        elif acao == "1":
            nova = console.input(
                f"  [{AMARELO}]➤[/{AMARELO}]  Nova pasta de destino: "
            ).strip()
            if nova:
                config.set("pasta_destino", nova)
        elif acao == "2":
            nova = console.input(
                f"  [{AMARELO}]➤[/{AMARELO}]  Qualidade padrão (ex: 1080, 720, 480): "
            ).strip()
            if nova:
                config.set("qualidade_padrao", nova)
        elif acao == "3":
            val = console.input(
                f"  [{AMARELO}]➤[/{AMARELO}]  Número de threads [1-16]: "
            ).strip()
            if val.isdigit():
                config.set("threads", max(1, min(int(val), 16)))
        elif acao == "5":
            proxy = console.input(
                f"  [{AMARELO}]➤[/{AMARELO}]  Proxy (ex: http://user:pass@host:port ou deixe vazio): "
            ).strip()
            config.set("proxy", proxy or None)
        elif acao == "6":
            atual = config.get("legendas", True)
            config.set("legendas", not atual)
            exibir_info(f"Legendas {'ativadas' if not atual else 'desativadas'}.")
        elif acao == "7":
            atual = config.get("thumbnails", True)
            config.set("thumbnails", not atual)
            exibir_info(f"Thumbnails {'ativadas' if not atual else 'desativadas'}.")
        elif acao == "8":
            atual = config.get("retomar", True)
            config.set("retomar", not atual)
            exibir_info(f"Retomar downloads {'ativado' if not atual else 'desativado'}.")
        elif acao == "9":
            lim = console.input(
                f"  [{AMARELO}]➤[/{AMARELO}]  Limite de velocidade (ex: 5M, 500K, ou vazio para ilimitado): "
            ).strip()
            config.set("limite_velocidade", lim or None)


def fluxo_perfis(config: ConfigManager):
    """Fluxo de gerenciamento de perfis."""
    while True:
        acao = exibir_tela_perfis(config.perfis)

        if acao == "V":
            break
        elif acao == "N":
            nome = console.input(f"  [{AMARELO}]➤[/{AMARELO}]  Nome do novo perfil: ").strip()
            if nome:
                qualidade = console.input(f"  [{AMARELO}]➤[/{AMARELO}]  Qualidade (ex: 1080): ").strip() or "1080"
                pasta = console.input(f"  [{AMARELO}]➤[/{AMARELO}]  Pasta de destino: ").strip()
                threads = console.input(f"  [{AMARELO}]➤[/{AMARELO}]  Threads [1-16]: ").strip()
                config.criar_perfil(nome, {
                    "qualidade": qualidade,
                    "formato": "mp4",
                    "threads": int(threads) if threads.isdigit() else 4,
                    "pasta_destino": pasta or str(Path.home() / "Downloads" / "ytdl-pro"),
                    "legendas": True,
                    "thumbnails": True,
                    "descricao": "Perfil personalizado",
                })
                exibir_sucesso(f"Perfil '{nome}' criado!")
        elif acao == "A":
            nome = console.input(f"  [{AMARELO}]➤[/{AMARELO}]  Nome do perfil para ativar: ").strip()
            if config.ativar_perfil(nome):
                exibir_sucesso(f"Perfil '{nome}' ativado!")
            else:
                exibir_erro(f"Perfil '{nome}' não encontrado.")
        elif acao == "D":
            nome = console.input(f"  [{AMARELO}]➤[/{AMARELO}]  Nome do perfil para deletar: ").strip()
            if config.deletar_perfil(nome):
                exibir_sucesso(f"Perfil '{nome}' deletado.")
            else:
                exibir_erro("Não é possível deletar o perfil 'Padrão' ou perfil não encontrado.")
        time.sleep(0.5)


def fluxo_cookies(config: ConfigManager):
    """Configuração de cookies para vídeos privados."""
    exibir_cabecalho("🍪  COOKIES / AUTENTICAÇÃO")

    console.print(f"  [{CIANO}]Navegador atual:[/] [{VERDE}]{config.get('cookies_navegador') or 'Nenhum'}[/]")
    console.print(f"  [{CIANO}]Arquivo atual:[/]   [{VERDE}]{config.get('cookies_arquivo') or 'Nenhum'}[/]\n")

    navegadores = ["chrome", "firefox", "edge", "opera", "safari", "brave", "chromium"]
    console.print(f"  [{AMARELO}]Navegadores suportados:[/] {', '.join(navegadores)}\n")

    nav = console.input(
        f"  [{AMARELO}]➤[/{AMARELO}]  Navegador (ou Enter para pular): "
    ).strip().lower()

    if nav in navegadores:
        config.set("cookies_navegador", nav)
        config.set("cookies_arquivo", None)
        exibir_sucesso(f"Cookies do {nav} configurados!")
    else:
        arq = console.input(
            f"  [{AMARELO}]➤[/{AMARELO}]  Caminho do arquivo cookies.txt (ou Enter para limpar): "
        ).strip()
        if arq and Path(arq).exists():
            config.set("cookies_arquivo", arq)
            config.set("cookies_navegador", None)
            exibir_sucesso("Arquivo de cookies configurado!")
        elif arq:
            exibir_erro("Arquivo não encontrado.")
        else:
            config.set("cookies_navegador", None)
            config.set("cookies_arquivo", None)
            exibir_info("Cookies removidos.")

    console.input(f"\n  [{CINZA}]Pressione ENTER para continuar...[/]")


# ── Loop principal do menu ────────────────────────────────────────────────────

def menu_principal():
    """Loop do menu principal interativo."""
    config = ConfigManager()
    config.gerar_env_exemplo()
    historico = HistoricoManager()
    motor = YTDLPro(config, historico)

    verificar_dependencias()

    while True:
        exibir_banner()
        perfis = config.nomes_perfis()
        escolha = exibir_menu_principal(perfis)

        if escolha == "1":
            fluxo_baixar_video(motor, config)
        elif escolha == "2":
            fluxo_baixar_playlist(motor, config)
        elif escolha == "3":
            fluxo_configuracoes(config)
        elif escolha == "4":
            fluxo_perfis(config)
        elif escolha == "5":
            exibir_cabecalho("📜  HISTÓRICO DE DOWNLOADS")
            exibir_tabela_historico(historico.todos())
            stats = historico.estatisticas()
            console.print(
                f"\n  Total: [{AMARELO}]{stats['total']}[/]  ·  "
                f"Sucesso: [{VERDE}]{stats['concluidos']}[/]  ·  "
                f"Erros: [{VERMELHO}]{stats['erros']}[/]"
            )
            opcao_limpar = console.input(
                f"\n  [{CINZA}]Limpar histórico? [s/N]:[/] "
            ).strip().lower()
            if opcao_limpar == "s":
                historico.limpar()
                exibir_sucesso("Histórico limpo!")
            console.input(f"\n  [{CINZA}]Pressione ENTER para continuar...[/]")
        elif escolha == "6":
            fluxo_cookies(config)
        elif escolha == "7":
            exibir_sobre()
        elif escolha == "0":
            console.print(
                f"\n  [{LARANJA}]Até logo! Obrigado por usar o YTDL-PRO. ✌[/]\n"
            )
            sys.exit(0)
        else:
            exibir_aviso("Opção inválida. Tente novamente.")
            time.sleep(0.8)


# ── CLI Click (comandos de linha de comando) ──────────────────────────────────

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    YTDL-PRO — Downloader profissional de vídeos e playlists do YouTube.

    Sem argumentos: abre o menu interativo.
    """
    if ctx.invoked_subcommand is None:
        menu_principal()


@cli.command("baixar")
@click.argument("url")
@click.option("--qualidade", "-q", default=None, help="Qualidade do vídeo (ex: 1080, 720, 480)")
@click.option("--pasta", "-p", default=None, help="Pasta de destino")
@click.option("--formato", "-f", default="mp4", help="Formato de saída (mp4, mp3, mkv)")
def cmd_baixar(url: str, qualidade: str, pasta: str, formato: str):
    """Baixa um vídeo diretamente sem menu interativo."""
    config = ConfigManager()
    historico = HistoricoManager()
    motor = YTDLPro(config, historico)

    if formato:
        config.set("formato", formato)

    exibir_banner()
    exibir_cabecalho("▶  BAIXAR VÍDEO (MODO DIRETO)")

    with spinner_buscando(url):
        info = motor.buscar_info(url)

    if info:
        exibir_info_video(info)

    motor.baixar_video(
        url=url,
        qualidade=qualidade or config.get("qualidade_padrao", "1080"),
        pasta_destino=pasta or config.get("pasta_destino"),
        numero=1,
        total=1,
        info_pre=info,
    )

    stats = motor.stats_sessao()
    exibir_resumo_final(stats)


@cli.command("playlist")
@click.argument("url")
@click.option("--qualidade", "-q", default=None, help="Qualidade dos vídeos")
@click.option("--pasta", "-p", default=None, help="Pasta base de destino")
@click.option("--inicio", "-i", default=1, help="Primeiro vídeo (padrão: 1)")
@click.option("--fim", "-e", default=None, type=int, help="Último vídeo (padrão: todos)")
def cmd_playlist(url: str, qualidade: str, pasta: str, inicio: int, fim: int):
    """Baixa uma playlist completa ou intervalo de vídeos."""
    config = ConfigManager()
    historico = HistoricoManager()
    motor = YTDLPro(config, historico)

    exibir_banner()
    exibir_cabecalho("📋  BAIXAR PLAYLIST (MODO DIRETO)")

    motor.baixar_playlist(
        url=url,
        qualidade=qualidade or config.get("qualidade_padrao", "1080"),
        pasta_destino=pasta or config.get("pasta_destino"),
        inicio=inicio,
        fim=fim,
    )

    stats = motor.stats_sessao()
    exibir_resumo_final(stats)


@cli.command("historico")
@click.option("--limpar", is_flag=True, help="Limpa o histórico completo")
def cmd_historico(limpar: bool):
    """Exibe ou limpa o histórico de downloads."""
    historico = HistoricoManager()

    if limpar:
        historico.limpar()
        exibir_sucesso("Histórico limpo com sucesso!")
        return

    exibir_banner()
    exibir_tabela_historico(historico.todos())
    stats = historico.estatisticas()
    console.print(
        f"\n  Total: [{AMARELO}]{stats['total']}[/]  ·  "
        f"Sucesso: [{VERDE}]{stats['concluidos']}[/]  ·  "
        f"Erros: [{VERMELHO}]{stats['erros']}[/]\n"
    )


@cli.command("config")
@click.option("--mostrar", is_flag=True, help="Mostra configuração atual em JSON")
@click.option("--reset", is_flag=True, help="Reseta para configuração padrão")
def cmd_config(mostrar: bool, reset: bool):
    """Gerencia a configuração do ytdl-pro."""
    import json
    from .config import CONFIG_FILE, CONFIG_PADRAO

    if reset:
        config = ConfigManager()
        config.config = dict(CONFIG_PADRAO)
        config.salvar()
        exibir_sucesso("Configuração resetada para os valores padrão!")
        return

    if mostrar:
        config = ConfigManager()
        console.print_json(json.dumps(config.config, indent=2, ensure_ascii=False))
        return

    config = ConfigManager()
    fluxo_configuracoes(config)


if __name__ == "__main__":
    cli()
