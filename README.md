# AI Calendar Agent (WhatsApp + FastAPI + OpenAI)

Este é um agente de Inteligência Artificial que integra o WhatsApp (via Evolution API) ao Google Calendar, permitindo agendamentos automáticos através de conversas naturais.

## 🚀 Funcionalidades
- **Verificação de Disponibilidade:** O agente consulta o calendário antes de sugerir ou marcar um horário.
- **Agendamento Inteligente:** Cria eventos no Google Calendar com resumo e descrição.
- **Processamento de Linguagem Natural:** Entende frases como "Tem horário dia 6 às 10h?" ou "Pode marcar para amanhã?".
- **Integração WhatsApp:** Recebe e envia mensagens através da Evolution API v2.

## 🛠️ Tecnologias
- **Python 3.10+**
- **FastAPI:** Framework para o Webhook.
- **OpenAI GPT-4o:** Cérebro do agente (com Function Calling).
- **Google Calendar API:** Manipulação da agenda.
- **Evolution API:** Interface com o WhatsApp.

## 📋 Pré-requisitos
1.  **Google Cloud Project:** Ativar Google Calendar API e baixar o `credentials.json`.
2.  **OpenAI API Key:** Gerar uma chave para o GPT-4o.
3.  **Evolution API:** Uma instância do WhatsApp conectada.
4.  **Ngrok:** Para exposição do webhook local (se for testar localmente).

## 🔧 Instalação e Configuração

1.  **Clonar o repositório e entrar na pasta:**
    ```bash
    cd CalendarAgent
    ```

2.  **Configurar ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variáveis de ambiente:**
    - Renomeie `.env.example` para `.env` e preencha suas chaves.

5.  **Credenciais do Google:**
    - Coloque o arquivo `credentials.json` na raiz do projeto.

## 🏃 Como Rodar Localmente

1.  **Iniciar o servidor:**
    ```bash
    # Com o venv ativado
    python main.py
    ```
2.  **Expor para a Internet (Ngrok):**
    Abra um **novo terminal** e rode:
    ```bash
    ngrok http 8000
    ```
    Copie a URL `https://...` gerada.

3.  **Configurar o Webhook:**
    - Na Evolution API, acesse as configurações da sua instância.
    - Na aba **Webhooks**, cole a URL do ngrok seguida de `/webhook`. Exemplo:
      `https://random-id.ngrok-free.app/webhook`
    - Ative o evento `MESSAGES_UPSERT`.

4.  **Autorizar o Google:** Na primeira execução, clique no link impresso no terminal do Python para autorizar o acesso à sua conta.

## 🤖 Exemplo de Fluxo
1.  **Usuário:** "Oi, tem horário livre dia 8 pela manhã?"
2.  **Agente:** (Verifica calendário) "Olá! No dia 8 tenho livre das 08:00 às 11:00. Algum desses horários funciona para você?"
3.  **Usuário:** "Pode marcar às 9h então."
4.  **Agente:** (Cria o evento) "Agendado! Marquei para o dia 8 às 09:00. Aqui está o link: [link]"
