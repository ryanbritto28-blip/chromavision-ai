from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, sys, logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app   = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
URL     = "https://api.openai.com/v1/chat/completions"
MODELO  = "gpt-4o-mini"
PORTA   = int(os.environ.get("PORT", 5000))

SYSTEM = """Você é a ChromaBot, assistente virtual do ChromaVision.
Responda SEMPRE em português brasileiro, de forma simpática e objetiva.
Máximo 3 frases por resposta.
Foque em daltonismo, acessibilidade visual e no app ChromaVision.

SOBRE O APP:
- Acessibilidade visual para pessoas com daltonismo
- PWA para Android e iPhone (instalar pelo navegador)
- Filtros: Protanopia, Deuteranopia, Tritanopia e Daltonize
- Plano gratuito disponível; Premium R$14,90/mês ou R$9,90/mês anual
- Contato: ChromaVision.project@gmail.com

DALTONISMO:
- Condição que afeta percepção de cores, origem genética
- Protanopia: dificuldade com vermelho
- Deuteranopia: dificuldade com verde (mais comum)
- Tritanopia: dificuldade com azul (mais rara)
- Cerca de 300 milhões de pessoas no mundo

CORES PARA VISÃO NORMAL:
- Vermelho: cor quente, energia e alerta
- Verde: cor natural, saúde e equilíbrio
- Azul: cor fria, tranquilidade e confiança
- Amarelo: cor luminosa, alegria e atenção"""


def perguntar(pergunta):
    if not API_KEY:
        log.error("OPENAI_API_KEY ausente")
        return "⚠️ Chave de API não configurada."
    try:
        log.info(f"Enviando para OpenAI. Modelo: {MODELO}")
        r = requests.post(URL,
            headers={"Authorization": f"Bearer {API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": MODELO,
                  "messages": [{"role": "system", "content": SYSTEM},
                                {"role": "user",   "content": pergunta}],
                  "max_tokens": 300,
                  "temperature": 0.7},
            timeout=30)
        log.info(f"OpenAI status: {r.status_code}")
        log.info(f"OpenAI body: {r.text[:300]}")
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "⚠️ A IA demorou para responder. Tente novamente."
    except requests.exceptions.HTTPError:
        log.error(f"HTTP {r.status_code}: {r.text[:300]}")
        return f"⚠️ Erro {r.status_code}. Verifique a chave da API."
    except Exception as e:
        log.error(f"Exceção: {e}")
        return f"⚠️ Erro: {str(e)}"


@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json()
    log.info(f"/chat recebido: {str(dados)[:100]}")
    if not dados or not dados.get("pergunta", "").strip():
        return jsonify({"erro": "Pergunta vazia."}), 400
    return jsonify({"resposta": perguntar(dados["pergunta"].strip())})


@app.route("/status")
def status():
    return jsonify({
        "servidor": "online",
        "api": "configurada" if API_KEY else "sem chave",
        "modelo": MODELO
    })


@app.route("/")
def raiz():
    return jsonify({"mensagem": "ChromaVision AI online.", "modelo": MODELO})


if __name__ == "__main__":
    log.info(f"Iniciando ChromaBot na porta {PORTA}")
    app.run(host="0.0.0.0", port=PORTA, debug=False)
