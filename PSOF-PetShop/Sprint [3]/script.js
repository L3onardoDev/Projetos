document.addEventListener('DOMContentLoaded', () => {
  const cartKey = 'petlife-cart';
  const accountKey = 'petlife-account';
  const sessionKey = 'petlife-session';
  const pendingProductKey = 'petlife-pending-product';
  const authKey = 'petlife-auth';
  const getCart = () => JSON.parse(localStorage.getItem(cartKey) || '[]');
  const saveCart = (cart) => localStorage.setItem(cartKey, JSON.stringify(cart));
  const money = (value) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

  const isLoggedIn = () => localStorage.getItem(sessionKey) === 'true';

  if (window.location.pathname.endsWith('Finalizacao.html') && !isLoggedIn()) {
    window.location.href = 'Login.html?redirect=Finalizacao.html';
    return;
  }

  const updateCartLabel = () => {
    const total = getCart().reduce((sum, item) => sum + item.quantity, 0);
    document.querySelectorAll('[data-cart-count]').forEach((element) => { element.textContent = total; });
  };

  const addToCart = (button) => {
    const product = button.closest('[data-product-card]');
    if (!product) return;
    const item = {
      name: product.dataset.name,
      price: Number(product.dataset.price),
      image: product.querySelector('img')?.getAttribute('src') || '',
      quantity: 1
    };
    if (!isLoggedIn()) {
      localStorage.setItem(pendingProductKey, JSON.stringify(item));
      window.location.href = 'Login.html?redirect=Carrinho.html';
      return;
    }
    const cart = getCart();
    const existing = cart.find((entry) => entry.name === item.name);
    if (existing) existing.quantity += 1;
    else cart.push(item);
    saveCart(cart);
    updateCartLabel();
    button.textContent = 'Adicionado';
    setTimeout(() => { button.textContent = 'Comprar'; }, 1400);
  };

  document.querySelectorAll('[data-product]').forEach((button) => {
    button.addEventListener('click', () => addToCart(button));
  });

  document.querySelectorAll('[data-checkout-link]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (!isLoggedIn()) {
        event.preventDefault();
        window.location.href = 'Login.html?redirect=Finalizacao.html';
      }
    });
  });

  // Busca simples no conteúdo visível da página.
  const search = document.querySelector('input[type="search"]');
  if (search) {
    search.addEventListener('input', () => {
      const term = search.value.trim().toLowerCase();
      document.querySelectorAll('.card').forEach((item) => {
        item.hidden = Boolean(term) && !item.textContent.toLowerCase().includes(term);
      });
    });
  }

  // Carrossel da página inicial.
  const bannerImage = document.querySelector('.banner img');
  const bannerButtons = document.querySelectorAll('.banner button');
  if (bannerImage && bannerButtons.length >= 2) {
    const banners = [
      { src: 'Assets/banner-1.jpg', alt: 'Produtos PetLife em destaque' },
      { src: 'Assets/banner-2.png', alt: 'Cuidados e produtos para pets' },
      { src: 'Assets/banner-3.png', alt: 'Ofertas PetLife' }
    ];
    let current = 0;
    const showBanner = (index) => {
      current = (index + banners.length) % banners.length;
      bannerImage.src = banners[current].src;
      bannerImage.alt = banners[current].alt;
    };
    bannerButtons[0].addEventListener('click', () => showBanner(current - 1));
    bannerButtons[1].addEventListener('click', () => showBanner(current + 1));
    setInterval(() => showBanner(current + 1), 6000);
  }

  // Filtros de categorias do catálogo.
  document.querySelectorAll('[data-filter]').forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      document.querySelectorAll('[data-category-section]').forEach((section) => {
        section.hidden = filter !== 'todos' && section.dataset.category !== filter;
      });
      document.querySelectorAll('[data-filter]').forEach((item) => item.classList.remove('ativo'));
      button.classList.add('ativo');
    });
  });

  // Cartões de suporte expansíveis.
  document.querySelectorAll('[data-help]').forEach((button) => {
    button.addEventListener('click', () => {
      const answer = button.parentElement.querySelector('.help-answer');
      const isOpen = answer.hidden;
      answer.hidden = !isOpen;
      button.textContent = isOpen ? 'Ocultar detalhes' : 'Ver detalhes';
    });
  });

  // Tela do carrinho: quantidade, remoção, total e avanço para checkout.
  const cartList = document.querySelector('[data-cart-list]');
  const cartEmpty = document.querySelector('[data-cart-empty]');
  const cartTotal = document.querySelector('[data-cart-total]');
  const renderCart = () => {
    if (!cartList) return;
    const cart = getCart();
    cartList.innerHTML = '';
    if (!cart.length) {
      cartEmpty.hidden = false;
      cartTotal.textContent = money(0);
      document.querySelector('[data-checkout-link]')?.classList.add('desabilitado');
      updateCartLabel();
      return;
    }
    cartEmpty.hidden = true;
    document.querySelector('[data-checkout-link]')?.classList.remove('desabilitado');
    cart.forEach((item, index) => {
      const row = document.createElement('article');
      row.className = 'cart-item';
      row.innerHTML = `
        <div><strong>${item.name}</strong><span>${money(item.price)} cada</span></div>
        <div class="cart-actions">
          <button type="button" data-cart-action="decrease" data-index="${index}" aria-label="Diminuir quantidade">−</button>
          <strong>${item.quantity}</strong>
          <button type="button" data-cart-action="increase" data-index="${index}" aria-label="Aumentar quantidade">+</button>
          <button type="button" data-cart-action="remove" data-index="${index}">Remover</button>
        </div>`;
      cartList.appendChild(row);
    });
    cartTotal.textContent = money(cart.reduce((sum, item) => sum + item.price * item.quantity, 0));
    updateCartLabel();
  };
  cartList?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-cart-action]');
    if (!button) return;
    const cart = getCart();
    const index = Number(button.dataset.index);
    if (button.dataset.cartAction === 'increase') cart[index].quantity += 1;
    if (button.dataset.cartAction === 'decrease') cart[index].quantity -= 1;
    if (button.dataset.cartAction === 'remove' || cart[index]?.quantity <= 0) cart.splice(index, 1);
    saveCart(cart);
    renderCart();
  });
  renderCart();

  // Checkout fictício: não há pagamento ou pedido real.
  const checkoutForm = document.querySelector('[data-checkout-form]');
  checkoutForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!isLoggedIn()) {
      window.location.href = 'Login.html?redirect=Finalizacao.html';
      return;
    }
    if (!getCart().length) return;
    const formData = Object.fromEntries(new FormData(checkoutForm).entries());
    const feedback = document.querySelector('[data-checkout-feedback]');
    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${JSON.parse(localStorage.getItem(authKey)).token}` },
        body: JSON.stringify({ ...formData, items: getCart() })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Não foi possível criar o pedido.');
      saveCart([]);
      document.querySelector('[data-checkout-panel]').hidden = true;
      document.querySelector('[data-order-success]').hidden = false;
      document.querySelector('[data-order-number]').textContent = result.order;
      updateCartLabel();
    } catch (error) {
      feedback.textContent = error.message;
      feedback.hidden = false;
    }
  });

  // Cadastro fictício do tutor e do pet.
  const petForm = document.querySelector('[data-pet-form]');
  petForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(petForm).entries());
    const feedback = document.querySelector('[data-pet-success]');
    try {
      const response = await fetch('/api/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Não foi possível criar o cadastro.');
      localStorage.setItem(accountKey, JSON.stringify(data));
      localStorage.removeItem(sessionKey);
      petForm.reset();
      feedback.className = 'feedback sucesso';
      feedback.textContent = result.message;
      feedback.hidden = false;
    } catch (error) {
      feedback.className = 'feedback erro';
      feedback.textContent = error.message;
      feedback.hidden = false;
    }
  });

  // Login fictício contra o cadastro salvo neste navegador.
  const loginForm = document.querySelector('[data-login-form]');
  loginForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(loginForm).entries());
    const feedback = document.querySelector('[data-login-feedback]');
    try {
      const response = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'E-mail ou senha inválidos.');
      localStorage.setItem(sessionKey, 'true');
      localStorage.setItem(authKey, JSON.stringify(result));
      const pendingProduct = JSON.parse(localStorage.getItem(pendingProductKey) || 'null');
      if (pendingProduct) {
        const cart = getCart();
        const existing = cart.find((entry) => entry.name === pendingProduct.name);
        if (existing) existing.quantity += 1;
        else cart.push(pendingProduct);
        saveCart(cart);
        localStorage.removeItem(pendingProductKey);
      }
      feedback.className = 'feedback sucesso';
      feedback.textContent = `Login realizado. Olá, ${result.user.ownerName}!`;
      const redirect = new URLSearchParams(window.location.search).get('redirect');
      if (redirect) setTimeout(() => { window.location.href = redirect; }, 700);
    } catch (error) {
      feedback.className = 'feedback erro';
      feedback.textContent = error.message;
      feedback.hidden = false;
    }
  });

  const bookingForm = document.querySelector('[data-booking-form]');
  bookingForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(bookingForm).entries());
    const protocol = `AT-${Date.now().toString().slice(-6)}`;
    localStorage.setItem('petlife-booking', JSON.stringify({ ...data, protocol }));
    const feedback = document.querySelector('[data-booking-success]');
    feedback.textContent = `Solicitação recebida! Protocolo ${protocol}. Nossa equipe confirmará o horário para ${data.pet}.`;
    feedback.hidden = false;
    bookingForm.reset();
  });

  updateCartLabel();
});
