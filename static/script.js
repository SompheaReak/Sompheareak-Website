<script>
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

// Update cart count everywhere
function updateCartCount(newCount) {
    document.querySelectorAll('#cart-count').forEach(el => el.innerText = newCount);
}

// Show and hide success message
function showSuccessMessage() {
    const success = document.getElementById('success');
    const sound = document.getElementById('success-sound');
    if (!success) return;

    if (sound) {
        sound.currentTime = 0;
        sound.play();
    }

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

// Auto-load next products when scrolling (optional)
function setupAutoLoadProducts() {
    const productCards = document.querySelectorAll('.product-card');
    if (!productCards.length) return;

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadMoreProducts();
                observer.disconnect();
            }
        });
    }, {
        rootMargin: "100px",
    });

    observer.observe(productCards[productCards.length - 1]);
}

function loadMoreProducts() {
    const hiddenProducts = document.querySelectorAll('.product-card[style*="display: none"]');
    hiddenProducts.forEach(card => {
        card.style.display = 'block';
    });
}

// Highlight current category or subcategory on page load
function highlightActiveCategory() {
    const currentUrl = window.location.href;
    document.querySelectorAll('.category-box a, .subcategory-box a').forEach(link => {
        if (currentUrl.includes(link.getAttribute('href'))) {
            link.classList.add('active');
        }
    });
}

// Handle full-screen image preview
function openImageModal(src) {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    modalImg.src = src;
    modal.style.display = 'flex';
}

function closeImageModal(event) {
    if (!event || event.target.id === 'image-modal' || event.target.classList.contains('close-button')) {
        document.getElementById('image-modal').style.display = 'none';
    }
}

// Handle Add to Cart without refreshing page
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('.add-to-cart-form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
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
                } else {
                    alert('Failed to add to cart');
                }
            })
            .catch(error => {
                console.error('Add to cart error:', error);
            });
        });
    });

    // Handle Next Subcategory button
    const button = document.getElementById('next-sub-btn');
    const grid = document.getElementById('product-grid');
    const currentInput = document.getElementById('current-subcategory');
    const listInput = document.getElementById('subcategory-list');

    if (button && grid && currentInput && listInput) {
        button.addEventListener('click', function () {
            const current = currentInput.value;
            const list = listInput.value.split(',').map(s => s.trim());
            const index = list.indexOf(current);

            if (index !== -1 && index < list.length - 1) {
                const nextSub = list[index + 1];

                fetch(`/subcategory/${encodeURIComponent(nextSub)}?ajax=true`)
                    .then(response => response.text())
                    .then(html => {
                        grid.insertAdjacentHTML('beforeend', html);
                        currentInput.value = nextSub;

                        // Highlight next subcategory
                        const subLinks = document.querySelectorAll('#subcategory-scroll a');
                        subLinks.forEach(a => {
                            a.classList.remove('active');
                            if (a.textContent.trim() === nextSub) {
                                a.classList.add('active');
                                a.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
                            }
                        });

                        if (index + 1 === list.length - 1) {
                            button.disabled = true;
                            button.textContent = 'បញ្ចប់ (No More Subcategories)';
                            button.style.backgroundColor = '#6c757d';
                            button.style.cursor = 'default';
                        }
                    })
                    .catch(err => {
                        console.error("Load error:", err);
                        alert('មានបញ្ហា នៅពេលបង្ហាញបន្ត!');
                    });
            } else {
                button.disabled = true;
                button.textContent = 'បញ្ចប់ (No More Subcategories)';
                button.style.backgroundColor = '#6c757d';
                button.style.cursor = 'default';
            }
        });
    }

    setupAutoLoadProducts();
    highlightActiveCategory();
});
</script>