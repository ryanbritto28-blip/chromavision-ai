"""
ChromaVision AI - ChromaBot
Arquitetura: Flask (Render.com) + Groq API (IA gratuita na nuvem)
Respostas em ~2 segundos, sem Ollama, sem computador ligado.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
MODELO       = "llama-3.1-8b-instant"   # Rápido, gratuito, ótimo em português
PORTA        = int(os.environ.get("PORT", 5000))

SYSTEM_PROMPT = """Você é a ChromaBot, assistente virtual oficial do ChromaVision.
Responda SEMPRE em português brasileiro, com tom simpático e objetivo.
Prefira respostas curtas — no máximo 3 parágrafos.
Se a pergunta não for sobre daltonismo, acessibilidade visual ou o ChromaVision,
redirecione gentilmente o usuário para esses temas.
Nunca invente funcionalidades que não existem.

=== IDENTIDADE ===
Nome: ChromaBot | App: ChromaVision
Missão: Promover inclusão e acessibilidade visual para pessoas com daltonismo.
Contato: ChromaVision.project@gmail.com

=== SOBRE O APP ===
- Acessibilidade visual para pessoas com daltonismo.
- Disponível como PWA para Android e iPhone (instale pelo navegador).
- Funciona offline nas funções básicas. Não substitui avaliação médica.
- Modo escuro e claro. Funciona em celular, tablet e computador.
- Não altera a foto original do usuário.
- Gratuito nas funções essenciais.
- Plano Mensal: R$14,90/mês. Plano Anual: R$9,90/mês.
- Vantagens premium: mais filtros, recursos avançados, armazenamento ampliado.

=== FUNCIONALIDADES ===
1. Simulação Protanopia (dificuldade com vermelho)
2. Simulação Deuteranopia (dificuldade com verde)
3. Simulação Tritanopia (dificuldade com azul)
4. Correção Daltonize (ajusta cores para facilitar distinção — não cura o daltonismo)
5. Upload de imagens da galeria
6. Modo escuro/claro

=== SOBRE DALTONISMO ===
- Condição que afeta a percepção das cores. Não é doença.
- Sem cura na maioria dos casos. Origem genética. Mais comum em homens.
- Cerca de 300 milhões de pessoas no mundo.
- Protanopia: cones do vermelho. Deuteranopia: cones do verde (mais comum).
- Tritanopia: cones do azul (mais rara). Acromatopsia: sem cores (muito rara).

=== DICAS PARA DESIGNERS ===
- Nunca use só cor para diferenciar informações. Adicione ícones ou padrões.
- Evite: vermelho+verde, verde+marrom, azul+roxo.
- Prefira: azul+laranja, preto+amarelo, azul+vermelho.
- Teste seus designs com o ChromaVision.

=== RESPOSTAS PADRÃO ===
Diagnóstico: O app não faz diagnóstico. Consulte um oftalmologista.
Foto alterada: Não. A imagem original fica intacta.
Instalar Android: Chrome → menu → Instalar app.
Instalar iPhone: Safari → compartilhar → Adicionar à Tela de Início.
Sugestões/erros: ChromaVision.project@gmail.com
"""


def perguntar_ao_modelo(pergunta: str) -> str:
    if not GROQ_API_KEY:
        return "⚠️ Chave da API não configurada. Fale com o administrador."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": pergunta}
        ],
        "temperature": 0.65,
        "max_tokens": 300,
    }

    try:
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "⚠️ A IA demorou para responder. Tente novamente."
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return "⚠️ Chave da API inválida. Verifique a configuração."
        return f"⚠️ Erro na API: {str(e)}"
    except Exception as e:
        return f"⚠️ Erro inesperado: {str(e)}"


@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json()
    if not dados or "pergunta" not in dados:
        return jsonify({"erro": "Campo 'pergunta' obrigatório."}), 400
    pergunta = dados["pergunta"].strip()
    if not pergunta:
        return jsonify({"erro": "Pergunta vazia."}), 400
    if len(pergunta) > 500:
        return jsonify({"erro": "Máximo 500 caracteres."}), 400
    return jsonify({"resposta": perguntar_ao_modelo(pergunta)})


@app.route("/status", methods=["GET"])
def status():
    groq_ok = bool(GROQ_API_KEY)
    return jsonify({
        "servidor": "online",
        "groq": "configurado" if groq_ok else "sem chave API",
        "modelo": MODELO
    })


@app.route("/", methods=["GET"])
def raiz():
    return jsonify({"mensagem": "ChromaVision AI online.", "modelo": MODELO})


if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("\n  ⚠️  GROQ_API_KEY não definida.")
        print("  Defina a variável de ambiente antes de iniciar.\n")
    print(f"\n  ChromaBot rodando em http://localhost:{PORTA}\n")
    app.run(host="0.0.0.0", port=PORTA, debug=False)
