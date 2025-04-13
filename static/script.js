function addToCart(productId) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.push(productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    alert('Added to cart!');
}

function switchLanguage() {
    const urlParams = new URLSearchParams(window.location.search);
    const lang = urlParams.get('lang') === 'en' ? 'kh' : 'en';
    window.location.search = `?lang=${lang}`;
}

document.addEventListener('DOMContentLoaded', () => {
    const cartItemsDiv = document.getElementById('cart-items');
    if (cartItemsDiv) {
        let cart = JSON.parse(localStorage.getItem('cart')) || [];
        cartItemsDiv.innerHTML = cart.length ? cart.map(id => `<p>Product ID: ${id}</p>`).join('') : '<p>Cart is empty.</p>';
    }
});
