import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

def agora_formatado():
    fuso_brasil = pytz.timezone("America/Sao_Paulo")
    return datetime.now(fuso_brasil).strftime("%d/%m/%Y %H:%M:%S")

# =========================
# CONFIGURAÇÕES GERAIS
# =========================

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

urls = [
    "https://inovax.com.br/",
    "https://inovax.com.br/login",
    "https://inovax.com.br/contato",
    "https://inovax.com.br/empresa",
    "https://inovax.com.br/suporte"
]

palavras_suspeitas = [
    "hacked",
    "malware",
    "eval(",
    "base64_decode",
    "shell_exec",
    "iframe",
    "script src=",
    "bitcoin",
    "defaced"
]

BASELINE_DIR = "baselines"
LOG_FILE = "alertas.log"

# =========================
# FUNÇÕES AUXILIARES
# =========================

def gerar_nome_arquivo(url):
    nome = url.replace("https://", "").replace("http://", "")
    nome = nome.replace("/", "_")
    return nome + ".txt"


def registrar_log(mensagem):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{data_hora}] {mensagem}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)


def obter_conteudo_limpo(url):
    resposta = requests.get(url, headers=headers, timeout=10)

    if resposta.status_code != 200:
        print(f"❌ Erro ao acessar {url} - Código {resposta.status_code}")
        return None

    soup = BeautifulSoup(resposta.text, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True).lower()


def detectar_palavras_suspeitas(conteudo):
    encontradas = []

    for palavra in palavras_suspeitas:
        if palavra.lower() in conteudo:
            encontradas.append(palavra)

    return encontradas

def detectar_palavras_suspeitas(conteudo):
    encontradas = []

    for palavra in palavras_suspeitas:
        if palavra.lower() in conteudo:
            encontradas.append(palavra)

    return encontradas


# NOVA FUNÇÃO TELEGRAM
def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ Variáveis do Telegram não configuradas")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": mensagem
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(" Mensagem enviada no Telegram")
        else:
            print("❌ Erro ao enviar Telegram:", response.text)
    except Exception as e:
        print("❌ Falha na requisição Telegram:", e)


def comparar_com_baseline(url):
    nome_arquivo = gerar_nome_arquivo(url)
    caminho = os.path.join(BASELINE_DIR, nome_arquivo)

    conteudo_atual = obter_conteudo_limpo(url)
    if conteudo_atual is None:
        return False

    if not os.path.exists(caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo_atual)
        print(f"📌 Baseline criado para {url}")
        return False

    with open(caminho, "r", encoding="utf-8") as f:
        conteudo_antigo = f.read().lower()

    # 🔥 ESSAS LINHAS ESTÃO FALTANDO NO SEU CÓDIGO
    alterado = conteudo_atual != conteudo_antigo
    palavras_encontradas = detectar_palavras_suspeitas(conteudo_atual)

    houve_alerta = False

    if alterado:
        mensagem = f"[{agora_formatado()}] ⚠ ALTERAÇÃO DETECTADA em {url}"
        print(f"⚠ {mensagem}")
        registrar_log(mensagem)
        enviar_telegram(mensagem)
        houve_alerta = True

    if palavras_encontradas:
        mensagem = f"[{agora_formatado()}] 🚨 PALAVRAS SUSPEITAS em {url}: {', '.join(palavras_encontradas)}"
        print(f"🚨 {mensagem}")
        registrar_log(mensagem)
        enviar_telegram(mensagem)
        houve_alerta = True

    if not alterado and not palavras_encontradas:
        print(f"✅ Nenhuma alteração em {url}")

    return houve_alerta

import time

INTERVALO = 60 * 60 * 12  # 12 horas

def executar_monitoramento():
    if not os.path.exists(BASELINE_DIR):
        os.makedirs(BASELINE_DIR)

    houve_algum_alerta = False

    for url in urls:
        resultado = comparar_com_baseline(url)
        if resultado:
            houve_algum_alerta = True

    if not houve_algum_alerta:
        mensagem = "✅ Monitoramento executado com sucesso. Nenhuma alteração detectada."
        print(mensagem)
        enviar_telegram(f"[{agora_formatado()}] ✅ Monitoramento executado. Nenhuma alteração detectada.")

def main():
    print("🚀 Monitoramento iniciado")

    while True:
        print("Nova verificação")
        executar_monitoramento()
        print("Aguardando 12 horas")
        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()



