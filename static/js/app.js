document.addEventListener('DOMContentLoaded', () => {
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 280) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        });

        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (event) {
            const href = this.getAttribute('href');
            if (!href || href === '#') {
                return;
            }
            const target = document.querySelector(href);
            if (!target) {
                return;
            }
            event.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    const revealTargets = document.querySelectorAll('.fade-in, .fade-up, .scroll-reveal');
    if (revealTargets.length && 'IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('appear', 'visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -40px 0px',
        });

        revealTargets.forEach((target) => revealObserver.observe(target));
    } else {
        revealTargets.forEach((target) => target.classList.add('appear', 'visible'));
    }

    document.querySelectorAll('.product-image').forEach((image) => {
        image.addEventListener('mouseenter', () => image.classList.add('scale-up'));
        image.addEventListener('mouseleave', () => image.classList.remove('scale-up'));
    });

    document.querySelectorAll('.cart-quantity-form').forEach((form) => {
        form.addEventListener('submit', () => {
            const card = form.closest('.cart-item-card') || form.closest('tr');
            if (card) {
                card.classList.add('highlight');
                setTimeout(() => card.classList.remove('highlight'), 900);
            }
        });
    });

    document.querySelectorAll('#checkoutForm input, #checkoutForm select, #checkoutForm textarea').forEach((field) => {
        field.addEventListener('focus', () => field.classList.add('focus-highlight'));
        field.addEventListener('blur', () => field.classList.remove('focus-highlight'));
    });

    document.querySelectorAll('.alert').forEach((message) => {
        setTimeout(() => {
            message.classList.add('fade');
            setTimeout(() => message.remove(), 600);
        }, 4000);
    });
});
