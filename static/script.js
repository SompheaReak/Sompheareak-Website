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
            });
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
    success.style.display = 'block';

    setTimeout(() => {
        success.style.animation = 'fadeout 0.5s forwards';
        setTimeout(() => {
            success.style.display = 'none';
            success.style.animation = ''; // reset animation for next time
        }, 500);
    }, 1500);
}