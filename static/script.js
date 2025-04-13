function increaseQuantity(button) {
    const input = button.parentElement.querySelector('input[name="quantity"]');
    input.value = parseInt(input.value) + 1;
}

function decreaseQuantity(button) {
    const input = button.parentElement.querySelector('input[name="quantity"]');
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
                    // Update cart count
                    document.getElementById('cart-count').innerText = data.cart_count;
                    // Show success message
                    const successDiv = document.getElementById('success');
                    successDiv.style.display = 'block';
                    setTimeout(() => {
                        successDiv.style.display = 'none';
                    }, 2000);
                }
            });
        });
    });
});