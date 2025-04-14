// script.js

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
        }, 500); // after fade out
    }, 1500); // show for 1.5 seconds
}