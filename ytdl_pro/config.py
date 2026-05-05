"""
Gerenciador de configurações — config.json + .env
"""

import json
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Diretório de configuração multiplataforma
CONFIG_DIR = Path.home() / ".config" / "ytdl-pro"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = CONFIG_DIR / ".env"
HISTORICO_FILE = CONFIG_DIR / "historico.json"

CONFIG_PADRAO: dict[str, Any] = {
    "pasta_destino": str(Path.home() / "Downloads" / "ytdl-pro"),
    "qualidade_padrao": "1080",
    "formato": "mp4",
    "threads": 4,
    "retomar": True,
    "legendas": True,
    "idioma_legendas": "pt",
    "thumbnails": True,
    "metadados": True,
    "cookies_navegador": None,  # "chrome", "firefox", "edge", etc.
    "cookies_arquivo": None,
    "limite_velocidade": None,  # ex: "5M" para 5MB/s
    "proxy": None,
    "formato_nome": "%(playlist_index)02d - %(title)s.%(ext)s",
    "formato_nome_simples": "%(title)s.%(ext)s",
    "subpasta_playlist": True,
    "perfil_ativo": "Padrão",
    "verificar_ffmpeg": True,
    "max_retentativas": 3,
    "timeout": 30,
    "user_agent": None,
}

PERFIS_PADRAO: dict[str, dict] = {
    "Padrão": {
        "qualidade": "1080",
        "formato": "mp4",
        "threads": 4,
        "pasta_destino": str(Path.home() / "Downloads" / "ytdl-pro"),
        "legendas": True,
        "thumbnails": True,
        "descricao": "Perfil equilibrado 1080p",
    },
    "Econômico": {
        "qualidade": "480",
        "formato": "mp4",
        "threads": 2,
        "pasta_destino": str(Path.home() / "Downloads" / "ytdl-pro" / "economico"),
        "legendas": False,
        "thumbnails": False,
        "descricao": "Menor tamanho de arquivo",
    },
    "Ultra HD": {
        "qualidade": "2160",
        "formato": "mp4",
        "threads": 6,
        "pasta_destino": str(Path.home() / "Downloads" / "ytdl-pro" / "4k"),
        "legendas": True,
        "thumbnails": True,
        "descricao": "Máxima qualidade disponível",
    },
    "Áudio": {
        "qualidade": "audio",
        "formato": "mp3",
        "threads": 4,
        "pasta_destino": str(Path.home() / "Downloads" / "ytdl-pro" / "audio"),
        "legendas": False,
        "thumbnails": True,
        "descricao": "Somente áudio em MP3",
    },
}


class ConfigManager:
    """Gerencia configuração persistente do ytdl-pro."""

    def __init__(self):
        self._garantir_diretorio()
        load_dotenv(ENV_FILE)
        self.config = self._carregar_config()
        self.perfis = self._carregar_perfis()

    def _garantir_diretorio(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _carregar_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                # Mescla com padrão para garantir novas chaves
                config = {**CONFIG_PADRAO, **dados}
                # Override com variáveis de ambiente
                config = self._aplicar_env(config)
                return config
            except (json.JSONDecodeError, IOError):
                pass
        config = dict(CONFIG_PADRAO)
        config = self._aplicar_env(config)
        self._salvar_config_arquivo(config)
        return config

    def _aplicar_env(self, config: dict) -> dict:
        """Aplica variáveis de ambiente sobre a config."""
        mapeamentos = {
            "YTDL_PASTA":          ("pasta_destino",    str),
            "YTDL_QUALIDADE":      ("qualidade_padrao", str),
            "YTDL_THREADS":        ("threads",          int),
            "YTDL_PROXY":          ("proxy",            str),
            "YTDL_VELOCIDADE":     ("limite_velocidade",str),
            "YTDL_COOKIES":        ("cookies_navegador",str),
            "YTDL_COOKIES_FILE":   ("cookies_arquivo",  str),
            "YTDL_USER_AGENT":     ("user_agent",       str),
        }
        for env_var, (chave, tipo) in mapeamentos.items():
            valor = os.getenv(env_var)
            if valor:
                try:
                    config[chave] = tipo(valor)
                except (ValueError, TypeError):
                    pass
        return config

    def _carregar_perfis(self) -> dict:
        perfis_file = CONFIG_DIR / "perfis.json"
        if perfis_file.exists():
            try:
                with open(perfis_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        self._salvar_perfis(PERFIS_PADRAO)
        return dict(PERFIS_PADRAO)

    def _salvar_config_arquivo(self, config: dict):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _salvar_perfis(self, perfis: dict):
        perfis_file = CONFIG_DIR / "perfis.json"
        with open(perfis_file, "w", encoding="utf-8") as f:
            json.dump(perfis, f, indent=2, ensure_ascii=False)

    def salvar(self):
        """Salva configuração atual no disco."""
        self._salvar_config_arquivo(self.config)

    def get(self, chave: str, padrao: Any = None) -> Any:
        return self.config.get(chave, padrao)

    def set(self, chave: str, valor: Any):
        self.config[chave] = valor
        self.salvar()

    def perfil_ativo(self) -> dict:
        nome = self.config.get("perfil_ativo", "Padrão")
        return self.perfis.get(nome, PERFIS_PADRAO["Padrão"])

    def ativar_perfil(self, nome: str) -> bool:
        if nome in self.perfis:
            perfil = self.perfis[nome]
            # Aplicar perfil na config global
            for chave in ("qualidade", "formato", "threads", "pasta_destino", "legendas", "thumbnails"):
                if chave in perfil:
                    chave_config = "qualidade_padrao" if chave == "qualidade" else chave
                    self.config[chave_config] = perfil[chave]
            self.config["perfil_ativo"] = nome
            self.salvar()
            return True
        return False

    def criar_perfil(self, nome: str, dados: dict):
        self.perfis[nome] = dados
        self._salvar_perfis(self.perfis)

    def deletar_perfil(self, nome: str) -> bool:
        if nome in self.perfis and nome != "Padrão":
            del self.perfis[nome]
            self._salvar_perfis(self.perfis)
            return True
        return False

    def nomes_perfis(self) -> list[str]:
        return list(self.perfis.keys())

    def gerar_env_exemplo(self):
        """Gera arquivo .env de exemplo se não existir."""
        if not ENV_FILE.exists():
            conteudo = """\
# YTDL-PRO — Variáveis de Ambiente
# Descomente e ajuste conforme necessário

# YTDL_PASTA=~/Downloads/ytdl-pro
# YTDL_QUALIDADE=1080
# YTDL_THREADS=4
# YTDL_PROXY=http://usuario:senha@proxy:8080
# YTDL_VELOCIDADE=5M
# YTDL_COOKIES=chrome
# YTDL_COOKIES_FILE=/caminho/para/cookies.txt
# YTDL_USER_AGENT=Mozilla/5.0 ...
"""
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write(conteudo)


class HistoricoManager:
    """Gerencia histórico de downloads."""

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.registros = self._carregar()

    def _carregar(self) -> list:
        if HISTORICO_FILE.exists():
            try:
                with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _salvar(self):
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
            json.dump(self.registros, f, indent=2, ensure_ascii=False)

    def adicionar(self, registro: dict):
        """Adiciona um registro ao histórico."""
        from datetime import datetime
        registro["data"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.registros.append(registro)
        # Manter apenas os últimos 1000
        if len(self.registros) > 1000:
            self.registros = self.registros[-1000:]
        self._salvar()

    def ja_baixado(self, video_id: str) -> dict | None:
        """Verifica se um vídeo já foi baixado pelo ID."""
        for reg in self.registros:
            if reg.get("video_id") == video_id and reg.get("status") == "ok":
                return reg
        return None

    def todos(self) -> list:
        return self.registros

    def limpar(self):
        self.registros = []
        self._salvar()

    def estatisticas(self) -> dict:
        total = len(self.registros)
        ok = sum(1 for r in self.registros if r.get("status") == "ok")
        erros = total - ok
        return {
            "total": total,
            "concluidos": ok,
            "erros": erros,
        }
