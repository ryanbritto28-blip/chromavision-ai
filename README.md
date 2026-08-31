# ChromaVision — Render + Gemini (gratuito)

Esta versão coloca o site e a API no mesmo Web Service do Render. A IA usa a Gemini API, com modelo `gemini-2.5-flash` por padrão.

## Estrutura
- `index.html` — aplicativo/PWA
- `main.py` — servidor Flask + API da ChromaBot
- `requirements.txt` — dependências
- `render.yaml` — configuração do Render
- `.python-version` — Python 3.13

## Deploy no Render
1. Crie um repositório no GitHub e envie TODOS os arquivos desta pasta para a raiz do repositório.
2. No Render: New → Web Service → conecte o repositório.
3. Use Free.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn main:app --bind 0.0.0.0:$PORT`
6. Em Environment, crie `GEMINI_API_KEY` e cole sua chave do Google AI Studio.
7. Crie/deploye o serviço.

## Google AI Studio
Crie uma chave de API no Google AI Studio. Não coloque a chave no `index.html` nem no GitHub.

## Teste
Abra:
- `/` → aplicativo
- `/api` → API online
- `/api/status` → status da IA

O frontend usa `/api/chat`, então não é necessário editar a URL do backend.
