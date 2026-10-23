# Backend do TR Video Downloader

API experimental em Python/FastAPI com yt-dlp. Funciona somente para links públicos acessíveis sem autenticação quando a plataforma permitir. Não contorna logins, DRM, restrições de acesso ou marcas d'água. Não garante suporte contínuo às plataformas.

## Publicação

1. Crie um serviço web Python em uma hospedagem que execute processos (GitHub Pages sozinho não executa Python).
2. Conecte este repositório e use `backend` como diretório raiz.
3. Comando de instalação: `pip install -r requirements.txt`
4. Comando de inicialização: `uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}`
5. Defina `SITE_ORIGIN=https://robinhodlx7-code.github.io`.
6. Configure a URL HTTPS da API na constante `API_BASE` do `index.html` (sem barra final).
7. Teste `https://SUA-API/health` e um vídeo público autorizado.

Atenção: planos gratuitos podem suspender serviços, restringir tráfego, disco e execução de yt-dlp. O código tem limites básicos por IP em memória, não adequados para tráfego público intenso ou múltiplas instâncias. Para produção, use rate limiting compartilhado, proteção contra bots, monitoramento, limite de saída de rede e isolamento do processo extrator. O download por yt-dlp pode acessar URLs de mídia externas descobertas na página; não trate este protótipo como uma solução de segurança auditada.
