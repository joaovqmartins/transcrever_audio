# Audio Transcriber

Aplicativo desktop simples e leve para transcrição de áudio, com interface
gráfica minimalista. Arraste um arquivo `.mp3` ou `.ogg`, clique em
**Transcrever** e receba o texto — a transcrição é feita pela **API de STT da
Groq**, que roda o modelo Whisper na nuvem com alta velocidade.

> **Atenção:** o app requer conexão com a internet e envia o arquivo de áudio
> para os servidores da Groq para ser transcrito. Se você precisa que o áudio
> nunca saia da sua máquina, esta versão não atende esse requisito.

## Índice

1. [O que é o projeto](#o-que-é-o-projeto)
2. [Requisitos](#requisitos)
3. [Instalar o Python](#instalar-o-python)
4. [Instalar as dependências](#instalar-as-dependências)
5. [Obter uma chave de API da Groq](#obter-uma-chave-de-api-da-groq)
6. [Como executar](#como-executar)
7. [Formatos suportados](#formatos-suportados)
8. [Limites da API](#limites-da-api)
9. [Escolhendo velocidade x precisão](#escolhendo-velocidade-x-precisão)
10. [Solução de problemas](#solução-de-problemas)

## O que é o projeto

Um MVP focado em um único fluxo: **arrastar áudio → transcrever na nuvem →
visualizar → copiar/salvar**. Sem login, sem banco de dados, sem servidor
próprio — só a interface local conversando com a API da Groq.

Estrutura do projeto:

```text
transcrever_audio/
├── main.py                        # ponto de entrada
├── requirements.txt
├── README.md
│
├── app/
│   ├── config.py                  # cores, modelos, idiomas
│   ├── ui/
│   │   ├── main_window.py         # interface gráfica (PySide6)
│   │   └── settings_dialog.py     # diálogo para configurar a chave de API
│   ├── transcription/
│   │   └── groq_engine.py         # motor de transcrição (API da Groq)
│   └── utils/
│       ├── audio.py               # validação de arquivos, tamanho
│       └── settings.py            # persistência local da chave de API
│
└── assets/
    └── icons/
```

## Requisitos

* Windows 10/11 (também funciona em macOS/Linux)
* Python 3.10 ou superior
* Conexão com a internet (necessária para toda transcrição, não só na primeira execução)
* Uma chave de API da Groq (gratuita)

## Instalar o Python

1. Baixe o instalador em [python.org/downloads](https://www.python.org/downloads/)
   (recomendado: versão 3.11.x ou 3.12.x).
2. Durante a instalação no Windows, marque a opção **"Add python.exe to PATH"**.
3. Verifique a instalação:

```bash
python --version
```

## Instalar as dependências

1. (Recomendado) Crie e ative um ambiente virtual dentro da pasta do projeto:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

Isso instala o **PySide6** (interface gráfica) e o **groq** (cliente oficial
da API de transcrição). São dependências leves — a instalação é rápida e não
baixa nenhum modelo de IA para o seu computador.

## Obter uma chave de API da Groq

1. Crie uma conta gratuita em [console.groq.com](https://console.groq.com/).
2. Acesse [console.groq.com/keys](https://console.groq.com/keys) e clique em
   **Create API Key**.
3. Copie a chave (começa com `gsk_...`).
4. Abra o Audio Transcriber, clique em **⚙ Configurações**, cole a chave no
   campo e clique em **Salvar**.

A chave é salva localmente em `%USERPROFILE%\.audio_transcriber\settings.json`
— nunca é enviada a nenhum lugar além da própria API da Groq.

## Como executar

Com o ambiente virtual ativado e as dependências instaladas:

```bash
python main.py
```

Fluxo de uso:

1. Abra o aplicativo e configure sua chave de API (só precisa fazer isso uma vez).
2. Arraste um arquivo `.mp3` ou `.ogg` para a área indicada (ou clique nela
   para selecionar manualmente).
3. Escolha o perfil de modelo e o idioma (ou deixe em "Detectar automaticamente").
4. Clique em **Transcrever**.
5. Acompanhe o status ("Enviando áudio...", "Transcrevendo...", etc.).
6. Copie ou salve o texto transcrito em `.txt`.

## Formatos suportados

Na primeira versão: **`.mp3`** e **`.ogg`**, enviados diretamente para a API
(a própria Groq decodifica o áudio, não é necessário FFmpeg local). Adicionar
outros formatos de entrada (ex.: `.wav`, `.m4a`) ou de exportação (`.srt`,
`.vtt`, `.json`) no futuro é uma extensão pontual — a lógica de exportação já
está separada da lógica de transcrição.

## Limites da API

* Tamanho máximo de arquivo: **25 MB** (definido em `MAX_FILE_SIZE_MB`, em
  [`app/config.py`](app/config.py)). Arquivos maiores são rejeitados com uma
  mensagem amigável antes de qualquer envio.
* A API da Groq tem uma camada gratuita com limites de uso (requisições por
  minuto/dia). Se você ultrapassar o limite, a API retorna um erro que é
  exibido na interface sem travar o aplicativo.

## Escolhendo velocidade x precisão

O combo **Modelo** na interface tem duas opções, definidas em
[`app/config.py`](app/config.py) (`MODEL_OPTIONS`):

* **Rápido** (`whisper-large-v3-turbo`) — mais barato e mais rápido, ótimo
  para a maioria dos áudios.
* **Preciso** (`whisper-large-v3`, padrão) — melhor qualidade de transcrição,
  recomendado quando precisão importa mais que velocidade ou custo.

Para adicionar ou ajustar perfis, basta editar a lista `MODEL_OPTIONS` em
`app/config.py` com o identificador de outro modelo suportado pela Groq —
nenhuma outra parte do código precisa mudar.

## Solução de problemas

* **"Nenhuma chave de API da Groq configurada"**: clique em
  **⚙ Configurações** e informe sua chave (veja
  [Obter uma chave de API da Groq](#obter-uma-chave-de-api-da-groq)).
* **"Chave de API inválida ou expirada"**: gere uma nova chave em
  [console.groq.com/keys](https://console.groq.com/keys) e atualize nas
  configurações do app.
* **"Não foi possível conectar à internet"**: verifique sua conexão — a
  transcrição não funciona offline nesta versão.
* **Arquivo acima do limite de 25 MB**: compacte o áudio (ex.: reduza o
  bitrate do MP3) ou corte o trecho relevante antes de enviar.
* **Mensagem de erro amigável na interface**: o aplicativo nunca fecha
  sozinho em caso de falha de transcrição; a mensagem de erro é exibida em
  uma janela e o app continua utilizável.
