function switchLanguage() {
    let currentUrl = window.location.href;
    if (currentUrl.includes('?lang=en')) {
        window.location.href = currentUrl.replace('?lang=en', '?lang=kh');
    } else if (currentUrl.includes('?lang=kh')) {
        window.location.href = currentUrl.replace('?lang=kh', '?lang=en');
    } else {
        window.location.href = currentUrl + '?lang=kh';
    }
}

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