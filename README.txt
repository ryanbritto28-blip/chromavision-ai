CHROMAVISION - VERCEL

Estrutura:
  api/index.py
  index.html
  manifest.json
  service-worker.js
  icon-192.png
  icon-512.png
  icon-maskable-512.png
  requirements.txt

Na Vercel:
1. Importe a pasta inteira.
2. Em Settings > Environment Variables, crie OPENAI_API_KEY com sua chave.
3. Faça Redeploy.
4. Teste /api/status e depois o ChromaBot.

A chave da OpenAI nunca deve ser colocada no index.html.
