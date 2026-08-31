from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'

SYSTEM = """Você é a ChromaBot, assistente virtual do ChromaVision.
Responda SEMPRE em português brasileiro, de forma simpática, clara e objetiva.
Normalmente use no máximo 4 frases, mas explique um pouco mais quando isso for necessário para responder corretamente.
Você é uma IA de verdade: raciocine sobre a pergunta, não invente informações e admita quando não souber.
Foque principalmente em daltonismo, acessibilidade visual, percepção de cores e no uso do aplicativo ChromaVision.

SOBRE O CHROMAVISION:
- Aplicativo de acessibilidade visual para pessoas com daltonismo.
- Funciona como PWA e pode ser instalado pelo navegador em Android e iPhone.
- Possui filtros para Protanopia, Deuteranopia, Tritanopia e Daltonize.
- O objetivo é ajudar o usuário a compreender e adaptar imagens e cores.
- O projeto possui plano gratuito e pode ter recursos Premium conforme a versão apresentada no aplicativo.
- Contato do projeto: ChromaVision.project@gmail.com

DALTONISMO:
- É uma alteração da percepção das cores, frequentemente de origem genética.
- Protanopia está relacionada principalmente à percepção do vermelho.
- Deuteranopia está relacionada principalmente à percepção do verde.
- Tritanopia está relacionada principalmente à percepção do azul.
- A intensidade e a experiência variam entre as pessoas.

REGRAS:
- Não dê diagnóstico médico.
- Não diga que uma pessoa é daltônica apenas por uma descrição ou foto.
- Quando a pergunta não tiver relação com o ChromaVision, ainda assim responda de forma útil, mas seja breve.
"""


def perguntar(pergunta: str) -> str:
    if not GEMINI_KEY:
        return '⚠️ A IA ainda não foi configurada no servidor. Falta cadastrar a GEMINI_API_KEY no Render.'

    payload = {
        'system_instruction': {'parts': [{'text': SYSTEM}]},
        'contents': [{'role': 'user', 'parts': [{'text': pergunta}]}],
        'generationConfig': {
            'maxOutputTokens': 500,
            'temperature': 0.6,
        },
    }

    try:
        r = requests.post(
            GEMINI_URL,
            params={'key': GEMINI_KEY},
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=45,
        )

        if r.status_code == 429:
            return '⚠️ A IA atingiu o limite gratuito momentâneo. Aguarde alguns segundos e tente novamente.'
        if r.status_code in (401, 403):
            return '⚠️ A chave da IA foi recusada. Verifique a GEMINI_API_KEY no Render.'
        if r.status_code >= 400:
            try:
                detail = r.json().get('error', {}).get('message', '')
            except Exception:
                detail = ''
            return f'⚠️ A IA não conseguiu responder agora. {detail}'.strip()

        data = r.json()
        candidates = data.get('candidates', [])
        if not candidates:
            return '⚠️ A IA não retornou uma resposta. Tente novamente.'

        parts = candidates[0].get('content', {}).get('parts', [])
        texto = ''.join(p.get('text', '') for p in parts).strip()
        return texto or '⚠️ A IA retornou uma resposta vazia.'

    except requests.exceptions.Timeout:
        return '⚠️ A IA demorou para responder. Tente novamente.'
    except requests.exceptions.RequestException:
        return '⚠️ Não foi possível conectar ao serviço de IA agora. Tente novamente.'
    except Exception:
        return '⚠️ O servidor encontrou um problema ao processar a pergunta.'


@app.get('/')
def home():
    return send_from_directory('.', 'index.html')


@app.post('/api/chat')
def chat():
    dados = request.get_json(silent=True) or {}
    pergunta = str(dados.get('pergunta', '')).strip()
    if not pergunta:
        return jsonify({'erro': 'Pergunta vazia.'}), 400
    return jsonify({'resposta': perguntar(pergunta)})


@app.get('/api/status')
def status():
    return jsonify({
        'servidor': 'online',
        'api': 'configurada' if GEMINI_KEY else 'sem chave',
        'modelo': MODEL,
        'provedor': 'Google Gemini',
    })


@app.get('/api')
def api_home():
    return jsonify({'mensagem': 'ChromaVision API online.', 'modelo': MODEL})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
