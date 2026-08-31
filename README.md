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

* Windows 10/11, Linux ou macOS
* Python 3.10 ou superior
* Conexão com a internet (necessária para toda transcrição, não só na primeira execução)
* Uma chave de API da Groq (gratuita)
* **No Linux:** as bibliotecas gráficas do Qt (veja [Instalar as dependências](#instalar-as-dependências) abaixo)

## Instalar o Python

**Windows:**

1. Baixe o instalador em [python.org/downloads](https://www.python.org/downloads/)
   (recomendado: versão 3.11.x ou 3.12.x).
2. Durante a instalação, marque a opção **"Add python.exe to PATH"**.
3. Verifique a instalação num terminal (PowerShell ou cmd):

```bash
python --version
```

**Linux:**

A maioria das distribuições já vem com Python 3 instalado, mas o pacote de
ambiente virtual (`venv`) às vezes precisa ser instalado à parte. Exemplo no
Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Em outras distros, use o gerenciador de pacotes equivalente (`dnf`, `pacman`,
etc.) para instalar `python3`, `python3-venv`/`python-virtualenv` e `pip`.

Verifique a instalação:

```bash
python3 --version
```

> **Atenção:** no Linux e no macOS o comando geralmente é `python3` (não
> `python`). Sempre que este README disser `python`, use `python3` nesses
> sistemas.

**macOS:**

```bash
brew install python
```

## Instalar as dependências

1. Crie e ative um ambiente virtual **dentro da pasta do projeto** — isso não
   é opcional: distribuições Linux recentes (Ubuntu 23.04+, Debian 12+)
   bloqueiam `pip install` fora de um venv por padrão, e é a causa mais comum
   do erro `ModuleNotFoundError: No module named 'groq'` ao tentar rodar o app.

```bash
# Windows (PowerShell ou cmd)
python -m venv venv
venv\Scripts\activate

# Linux ou macOS
python3 -m venv venv
source venv/bin/activate
```

   Depois de ativado, o início da linha do terminal deve mostrar `(venv)`.
   Confirme que o `pip` do venv está sendo usado:

```bash
# Linux/macOS
which python
# deve terminar em algo como .../transcrever_audio/venv/bin/python
```

2. Instale as dependências (com o venv **ainda ativado**):

```bash
pip install -r requirements.txt
```

Isso instala o **PySide6** (interface gráfica) e o **groq** (cliente oficial
da API de transcrição). São dependências leves — a instalação é rápida e não
baixa nenhum modelo de IA para o seu computador.

3. Confirme que as dependências foram instaladas corretamente:

```bash
python -c "import groq, PySide6; print('OK')"
```

Se aparecer `ModuleNotFoundError` aqui, o venv não está ativado (repita o
passo 1) ou a instalação do passo 2 falhou — role a tela para cima e veja se
o `pip install` mostrou algum erro.

### Bibliotecas gráficas do Qt no Linux

O PySide6 depende de bibliotecas do sistema para abrir janelas (plugin
`xcb`/Wayland). Se o app não abrir e o erro mencionar `xcb`, `Could not load
the Qt platform plugin` ou `libEGL`/`libGL`, instale os pacotes do sistema
(exemplo no Ubuntu/Debian):

```bash
sudo apt install libxcb-cursor0 libxcb-xinerama0 libgl1
```

Em outras distros, procure pelo pacote equivalente a `libxcb-cursor0` (ex.:
`xcb-util-cursor` no Fedora/Arch).

## Obter uma chave de API da Groq

1. Crie uma conta gratuita em [console.groq.com](https://console.groq.com/).
2. Acesse [console.groq.com/keys](https://console.groq.com/keys) e clique em
   **Create API Key**.
3. Copie a chave (começa com `gsk_...`).
4. Abra o Audio Transcriber, clique no ícone de cadeado (🔒) no canto
   superior direito, cole a chave no campo e clique em **Salvar**.

A chave é salva localmente — nunca é enviada a nenhum lugar além da própria
API da Groq:

* Windows: `%USERPROFILE%\.audio_transcriber\settings.json`
* Linux/macOS: `~/.audio_transcriber/settings.json`

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

* **`ModuleNotFoundError: No module named 'groq'`** (ou `PySide6`): o
  ambiente virtual não está ativado, ou as dependências não foram instaladas
  nele. No Linux/macOS, rode `source venv/bin/activate` (Windows:
  `venv\Scripts\activate`) e depois `pip install -r requirements.txt`
  novamente — confira com `which python` (Linux/macOS) que ele aponta para
  dentro da pasta `venv`. Veja [Instalar as dependências](#instalar-as-dependências).
* **`pip install` falha com "externally-managed-environment"** (comum em
  Ubuntu/Debian recentes): é o sistema bloqueando instalação de pacotes fora
  de um venv — não use `--break-system-packages`, apenas crie e ative o
  ambiente virtual como descrito acima antes de instalar.
* **`command not found: python`** no Linux/macOS: use `python3` no lugar de
  `python` (o comando `python` sozinho geralmente não existe nessas
  plataformas).
* **Erro mencionando `xcb`, `Could not load the Qt platform plugin` ou
  `libEGL`/`libGL`** no Linux: faltam bibliotecas gráficas do sistema — veja
  [Bibliotecas gráficas do Qt no Linux](#bibliotecas-gráficas-do-qt-no-linux).
* **"Nenhuma chave de API da Groq configurada"**: clique no ícone de cadeado
  e informe sua chave (veja
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
