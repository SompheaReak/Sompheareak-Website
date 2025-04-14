// Handle quantity increase/decrease
function increaseQuantity(button) {
    const input = button.parentNode.querySelector('input[name="quantity"]');
    input.value = parseInt(input.value) + 1;
}

function decreaseQuantity(button) {
    const input = button.parentNode.querySelector('input[name="quantity"]');
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

// Handle Add to Cart without refreshing page
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.add-to-cart-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch('/add-to-cart', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartCount(data.cart_count);
                    showSuccessMessage();
                }
            })
            .catch(error => console.error('Error adding to cart:', error));
        });
    });

    // Handle auto-load subcategories
    setupAutoLoadProducts();
});

// Update cart count everywhere
function updateCartCount(newCount) {
    document.querySelectorAll('#cart-count').forEach(el => el.innerText = newCount);
}

// Show and hide success message
function showSuccessMessage() {
    const success = document.getElementById('success');
    if (!success) return;
    success.style.display = 'block';
    success.style.opacity = '1';
    success.style.transition = 'opacity 0.5s ease';

    setTimeout(() => {
        success.style.opacity = '0';
        setTimeout(() => {
            success.style.display = 'none';
        }, 500);
    }, 1500);
}

// Auto-load next products when scroll
function setupAutoLoadProducts() {
    const productCards = document.querySelectorAll('.product-card');
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadMoreProducts();
                observer.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: "100px",
    });

    if (productCards.length) {
        observer.observe(productCards[productCards.length - 1]);
    }
}

function loadMoreProducts() {
    const hiddenProducts = document.querySelectorAll('.product-card[style*="display: none"]');
    hiddenProducts.forEach(card => {
        card.style.display = 'block';
    });
}