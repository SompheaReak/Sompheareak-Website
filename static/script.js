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
});

    setupAutoLoadProducts();
    highlightActiveCategory();
});

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

// Auto-load next products when scrolling
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

// Highlight current category or subcategory
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