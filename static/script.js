<script>
// Quantity controls
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

// Success Message
function updateCartCount(newCount) {
    document.querySelectorAll('#cart-count').forEach(el => el.innerText = newCount);
}
function showSuccessMessage() {
    const success = document.getElementById('success');
    const sound = document.getElementById('success-sound');
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

// Load More (Optional Lazy Load)
function setupAutoLoadProducts() {
    const cards = document.querySelectorAll('.product-card');
    if (!cards.length) return;

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadMoreProducts();
                observer.disconnect();
            }
        });
    }, { rootMargin: "100px" });

    observer.observe(cards[cards.length - 1]);
}
function loadMoreProducts() {
    document.querySelectorAll('.product-card[style*="display: none"]').forEach(card => {
        card.style.display = 'block';
    });
}

// Fullscreen Modal
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

// Category/subcategory highlighting
function highlightActiveCategory() {
    const currentUrl = window.location.href;
    document.querySelectorAll('.category-box a, .subcategory-box a').forEach(link => {
        if (currentUrl.includes(link.getAttribute('href'))) {
            link.classList.add('active');
        }
    });
}

// Add to Cart
function bindAddToCartHandlers() {
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
                    alert('បន្ថែមទៅកន្ត្រកមិនបានទេ!');
                }
            })
            .catch(error => {
                console.error('Add to cart error:', error);
                alert('មានបញ្ហា នៅពេលបន្ថែមទៅកន្ត្រក!');
            });
        });
    });
}

// Subcategory load button
function setupNextSubcategoryButton() {
    const button = document.getElementById('next-sub-btn');
    const grid = document.getElementById('product-grid');
    const currentInput = document.getElementById('current-subcategory');
    const listInput = document.getElementById('subcategory-list');

    if (!button || !grid || !currentInput || !listInput) return;

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
                    document.querySelectorAll('#subcategory-scroll a').forEach(a => {
                        a.classList.remove('active');
                        if (a.textContent.trim() === nextSub) {
                            a.classList.add('active');
                            a.scrollIntoView({ behavior: 'smooth', inline: 'center' });
                        }
                    });
                    bindAddToCartHandlers();
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
        }
    });
}

// Slideshow
function setupSlider() {
    let slideIndex = 0;
    const slidesWrapper = document.getElementById('slides');
    const slides = slidesWrapper.querySelectorAll('.slide');
    const dotsContainer = document.getElementById('dots');

    // Create dots
    slides.forEach((_, i) => {
        const dot = document.createElement('span');
        dot.classList.add('dot');
        dot.addEventListener('click', () => goToSlide(i));
        dotsContainer.appendChild(dot);
    });

    function updateDots() {
        const dots = dotsContainer.querySelectorAll('.dot');
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === slideIndex);
        });
    }

    function showSlide() {
        slidesWrapper.style.transform = `translateX(-${slideIndex * 100}%)`;
        updateDots();
    }

    function goToSlide(n) {
        slideIndex = n;
        showSlide();
    }

    function autoSlide() {
        slideIndex = (slideIndex + 1) % slides.length;
        showSlide();
    }

    showSlide();
    setInterval(autoSlide, 4000);
}

// DOM Ready
document.addEventListener('DOMContentLoaded', function () {
    bindAddToCartHandlers();
    setupNextSubcategoryButton();
    setupAutoLoadProducts();
    highlightActiveCategory();
    setupSlider();
});
</script>