<<<<<<< HEAD
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
=======
# 🎓 Projetos SENAI

Este repositório reúne os projetos, exercícios práticos e atividades desenvolvidas durante minha trajetória no **SENAI (Serviço Nacional de Aprendizagem Industrial)**. O objetivo principal é documentar meu aprendizado técnico, evolução prática e aplicação de conhecimentos nas áreas de desenvolvimento e tecnologia.

---

## 🛠️ Tecnologias e Ferramentas

| Categoria | Tecnologias Utilizadas |
| :--- | :--- |
| **Linguagens** | HTML5, CSS3, JavaScript, Python, C# |
| **Frameworks / Libs** | React, Node.js, Bootstrap |
| **Bancos de Dados** | MySQL, PostgreSQL |
| **Ferramentas & Outros** | Git, GitHub, VS Code, Figma |

---

## 📂 Estrutura do Repositório

```text
├── 📁 PSOF-PetShop/      # Projeto Academico - PetShop
```

---

## 🚀 Projetos em Destaque

### 1. PSOF-PetShop
* **Descrição:** Aplicação web para gerenciamento e agendamento de serviços de pet shop, facilitando a navegação de tutores por serviços e banho/tosa, além de otimizar a organização de atendimentos.
* **Competências praticadas:** Manipulação do DOM, design responsivo, gerenciamento de estado simples e integração com APIs para simulação de agendamentos.
* **Tecnologias: HTML, CSS, JavaScript.**
---

## 🔧 Como Executar os Projetos

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   ```

2. **Navegue até a pasta do projeto desejado:**
   ```bash
   cd nome-do-repositorio/pasta-do-projeto
   ```

3. **Execução:**
   Siga as instruções específicas de execução presentes no arquivo `README.md` localizado dentro da pasta de cada projeto ou abra o arquivo `index.html` diretamente no seu navegador.

---

## 📄 Licença

Este repositório está sob a licença [MIT](./LICENSE) — sinta-se à vontade para utilizar os códigos como referência para estudos.

---

<div align="center">
  <sub>Desenvolvido com dedicação por <strong>Leonardo Barbosa</strong> durante as aulas no SENAI.</sub>
</div>
>>>>>>> bd0968dc74611480b545097058bbf60eb054443c
