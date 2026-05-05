"""
UI simplificada para Textual - apenas print
"""

VERDE = "\033[92m"
LARANJA = "\033[38;5;208m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
CIANO = "\033[96m"
CINZA = "\033[90m"
BRANCO = "\033[97m"
ROXO = "\033[95m"
AZUL = "\033[94m"
RESET = "\033[0m"

def exibir_sucesso(msg: str):
    print(f"{VERDE}✓ {msg}{RESET}")

def exibir_erro(msg: str):
    print(f"{VERMELHO}✗ {msg}{RESET}")

def exibir_aviso(msg: str):
    print(f"{AMARELO}⚠ {msg}{RESET}")

def exibir_info(msg: str):
    print(f"{CIANO}ℹ {msg}{RESET}")

def criar_progresso_download():
    return None

def exibir_confirmacao_duplicata(titulo: str, caminho: str) -> str:
    print(f"{AMARELO}⚠ Arquivo já existe: {titulo}{RESET}")
    print(f"  {CINZA}{caminho}{RESET}")
    print(f"  [S] Substituir, [P] Pular, [R] Renomear, [T] Todos")
    escolha = input("  Escolha: ").strip().upper()
    return escolha if escolha in ("S", "P", "R", "T") else "P"

console = None
AZUL = CIANO