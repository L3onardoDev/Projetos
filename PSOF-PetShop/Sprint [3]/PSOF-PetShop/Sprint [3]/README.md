# PetLife — projeto demonstrativo

O projeto agora simula uma pequena loja PetLife sem realizar vendas reais.

## Funcionalidades

O catálogo permite adicionar produtos ao carrinho. A tela de carrinho mostra os itens, permite aumentar ou diminuir quantidades, remover produtos, recalcular o total e avançar para `Finalizacao.html`.

A tela de finalização coleta dados fictícios de entrega e uma forma de pagamento apenas para demonstrar o fluxo. Ao confirmar, gera um número de pedido simulado e limpa o carrinho; nenhuma cobrança é feita.

As telas `Cadastro_Pet.html` e `Login.html` simulam o cadastro do tutor e do pet e a entrada na conta. Os dados são salvos somente no `localStorage` do navegador usado na demonstração.

A compra exige autenticação: ao clicar em Comprar sem login, o usuário é enviado para o login e o produto escolhido fica reservado. Depois do login, ele é incluído automaticamente no carrinho e o usuário retorna para continuar a compra. O acesso à finalização também é protegido.

## Banco de dados

Para este protótipo, **não é necessário banco de dados**. O carrinho, o cadastro e o login são apenas demonstrações locais.

Um banco será necessário se o projeto evoluir para uma aplicação real com usuários persistentes, pedidos, estoque, pagamentos, produtos gerenciados por painel administrativo, blog editável ou armazenamento permanente de formulários.

## Banco de dados local

O arquivo `server.py` cria automaticamente o banco `petlife.db` usando SQLite. Ele cria as tabelas `users`, `pets`, `products`, `orders` e `order_items`, além de inserir os produtos iniciais.

Para executar o projeto com o banco ativo, use `python3 server.py` dentro desta pasta e abra `http://localhost:4173`. O cadastro, login e checkout passam a usar as rotas `/api/register`, `/api/login` e `/api/orders`.
