# PetLife

Site de pet shop com catálogo de produtos, carrinho de compras, cadastro de tutores e pets, solicitação de agendamentos e registro de pedidos. O projeto combina páginas em HTML, CSS e JavaScript com uma API em Python e banco de dados SQLite.

## Funcionalidades

- Catálogo com busca e filtros por categoria.
- Carrinho persistido no navegador, com ajuste de quantidades e remoção de itens.
- Cadastro e login de tutores, com os dados do tutor e de seu pet.
- Senhas protegidas com PBKDF2; sessões com validade de sete dias.
- Pedidos associados à conta do tutor. O servidor consulta os preços do catálogo e calcula o total.
- Solicitações de banho e tosa com protocolo de atendimento.
- Suporte centralizado em chatbot com API de IA.
- Interface adaptada para navegação em dispositivos móveis.

> **Pagamento:** o checkout registra o pedido, mas não processa pagamentos online. Não informe dados reais de pagamento. Uma integração com um provedor de pagamentos deverá ser implementada antes de aceitar cobranças.

## Tecnologias

- HTML, CSS e JavaScript no frontend.
- Python 3 na API e no servidor HTTP.
- SQLite para persistência dos dados.

O backend usa apenas a biblioteca padrão do Python; não é necessário instalar dependências Python adicionais.

## Requisitos

- Python 3 instalado.
- Navegador atualizado.

## Como executar

Abra um terminal nesta pasta do projeto e inicie o servidor:

```bash
python server.py
```

Em ambientes nos quais o comando `python` aponta para uma versão diferente, use o comando Python 3 disponível, por exemplo:

```bash
python3 server.py
```

Depois, acesse <http://localhost:4173>. Mantenha o terminal aberto enquanto utiliza o site. Não abra os arquivos HTML diretamente com `file://`, pois cadastro, login, pedidos e agendamentos precisam da API.

Para verificar se o servidor e o banco estão disponíveis, acesse <http://localhost:4173/api/health>.

## Páginas

| Arquivo | Conteúdo |
| --- | --- |
| `index.html` | Página inicial |
| `Catálogo_Produtos.html` | Catálogo de produtos |
| `Carrinho.html` | Carrinho de compras |
| `Finalizacao.html` | Dados de entrega e registro do pedido |
| `Cadastro_Pet.html` | Cadastro do tutor e do pet |
| `Login.html` | Login |
| `Agendamento.html` | Solicitação de agendamento |
| `Servicos.html` | Serviços |
| `Perguntas_Frequentes.html` | Perguntas frequentes |
| `Suporte-Atendimento.html` | Suporte e atendimento |

## API

O servidor disponibiliza os seguintes endpoints:

| Método | Endpoint | Descrição |
| --- | --- | --- |
| `GET` | `/api/health` | Verifica a disponibilidade da API e do banco |
| `GET` | `/api/products` | Retorna os produtos e o estoque |
| `POST` | `/api/register` | Cadastra tutor e pet |
| `POST` | `/api/login` | Autentica o tutor e cria uma sessão |
| `POST` | `/api/orders` | Registra um pedido; exige sessão válida |
| `POST` | `/api/bookings` | Registra uma solicitação de agendamento |
| `POST` | `/api/chat` | Consulta o assistente Grok; exige `XAI_API_KEY` no servidor |

As operações `POST` recebem dados em JSON.

## Configurar o chatbot

A página `Suporte-Atendimento.html` usa o chat como elemento principal e não expõe a chave de API no navegador. O backend carrega automaticamente um arquivo `.env` colocado na mesma pasta do `server.py`. Para usar o Groq, crie esse arquivo com:

```env
XAI_API_KEY=sua-chave-groq-aqui
XAI_CHAT_MODEL=llama-3.1-8b-instant
XAI_API_BASE=https://api.groq.com/openai/v1
```

Para continuar usando Grok, use `grok-3-mini` e `https://api.x.ai/v1` no lugar dos valores do Groq. Nunca coloque a chave diretamente em `script.js` ou em um arquivo HTML. O arquivo `.env` não deve ser publicado ou compartilhado.

As telas `Servicos.html`, `Login.html` e `Cadastro_Pet.html` foram reorganizadas com hierarquia visual, cartões mais claros, chamadas de ação, benefícios da conta, etapas de preenchimento, mostrar/ocultar senha e layout responsivo.

## Banco de dados

Na inicialização, o servidor cria ou atualiza `petlife.db` na pasta do projeto. O banco contém as tabelas de tutores (`users`), pets (`pets`), produtos (`products`), pedidos (`orders`), itens dos pedidos (`order_items`), agendamentos (`bookings`) e sessões (`sessions`).

Os produtos iniciais são inseridos sem duplicar os que já existem, e sessões expiradas são removidas. Antes de atualizar uma instalação com dados que deseja manter, faça uma cópia de segurança do arquivo `petlife.db`.

## Estrutura principal

```text
Sprint [3]/
├── Assets/                 # Imagens e ícones
├── *.html                  # Páginas do site
├── script.js               # Interações do frontend e chamadas à API
├── style.css               # Estilos
├── server.py               # Servidor HTTP, API e inicialização do SQLite
└── petlife.db              # Banco de dados SQLite
```

## Publicação

O servidor está configurado para escutar em todas as interfaces de rede na porta `4173`. Para disponibilizá-lo fora do ambiente local, configure uma hospedagem apropriada, HTTPS, armazenamento persistente e backups. Avalie também os requisitos de privacidade, retenção e proteção dos dados pessoais antes de usar informações reais.
<!-- d -->
