# PetLife — site e banco de dados

Site PetLife com catálogo de produtos, carrinho, cadastro de tutores e pets, agendamento de serviços e registro de pedidos.

## Funcionalidades

- Catálogo e carrinho de compras. O carrinho permanece salvo no navegador.
- Cadastro e login de tutores, com sessões persistidas e senhas armazenadas em hash PBKDF2.
- Cadastro dos pets associados ao tutor.
- Pedidos e respectivos itens gravados no SQLite; preços e totais são conferidos e calculados no servidor.
- Solicitações de agendamento gravadas no banco com protocolo.

## Banco de dados

O servidor cria e atualiza `petlife.db` automaticamente ao iniciar, usando SQLite e sem dependências externas. As tabelas são `users`, `pets`, `products`, `orders`, `order_items`, `bookings` e `sessions`.

Na inicialização, os produtos do catálogo são incluídos apenas quando ainda não existem, registros órfãos de pets são removidos e sessões expiradas são descartadas. Faça uma cópia de segurança de `petlife.db` antes de atualizar uma instalação com dados reais.

## Execução

Na pasta do projeto, execute:

```bash
python3 server.py
```

Abra `http://localhost:4173`. O endpoint `http://localhost:4173/api/health` informa se a API e o banco estão disponíveis. Não abra as páginas diretamente como `file://`: cadastro, login, pedidos e agendamentos dependem da API.

## Pagamento e publicação

Os pedidos são registrados no banco. O pagamento online ainda não é processado; antes de aceitar pagamentos pela internet, conecte e valide uma integração com um provedor de pagamentos. Para publicação, configure HTTPS, hospedagem persistente e backups; avalie também os requisitos de privacidade, retenção de dados e gestão de estoque.
