document.addEventListener('DOMContentLoaded', () => {

    // ========================
    // 1. Back to Top Button
    // ========================
    const backToTop = document.getElementById('backToTop');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('show');
        } else {
            backToTop.classList.remove('show');
        }
    });
    backToTop.addEventListener('click', () => {
        window.scrollTo({top:0, behavior:'smooth'});
    });

    // ========================
    // 2. Smooth Scrolling for Nav Links
    // ========================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if(target){
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ========================
    // 3. Fade-in Animation on Scroll (for index.html sections)
    // ========================
    const faders = document.querySelectorAll('.fade-in, .fade-up');
    const appearOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };
    const appearOnScroll = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if(entry.isIntersecting){
                entry.target.classList.add('appear');
                observer.unobserve(entry.target);
            }
        });
    }, appearOptions);

    faders.forEach(fader => appearOnScroll.observe(fader));

    // ========================
    // 4. Product Image Hover Animation (product.html)
    // ========================
    const productImages = document.querySelectorAll('.product-image');
    productImages.forEach(img => {
        img.addEventListener('mouseenter', () => img.classList.add('scale-up'));
        img.addEventListener('mouseleave', () => img.classList.remove('scale-up'));
    });

    // ========================
    // 5. Cart Quantity Animation (cart.html)
    // ========================
    const quantityForms = document.querySelectorAll('.cart-quantity-form');
    quantityForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = form.querySelector('input[name="quantity"]');
            const value = input.value;
            const row = form.closest('tr');
            row.classList.add('highlight');
            setTimeout(() => row.classList.remove('highlight'), 800);
            form.submit(); // submit after animation
        });
    });

    // ========================
    // 6. Checkout Form Highlight on Focus (checkout.html)
    // ========================
    const checkoutInputs = document.querySelectorAll('#checkoutForm input, #checkoutForm select, #checkoutForm textarea');
    checkoutInputs.forEach(input => {
        input.addEventListener('focus', () => input.classList.add('focus-highlight'));
        input.addEventListener('blur', () => input.classList.remove('focus-highlight'));
    });

    // ========================
    // 7. Flash Message Auto Fade-out
    // ========================
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add('fade');
            setTimeout(()=> msg.remove(), 600);
        }, 4000);
    });

});
