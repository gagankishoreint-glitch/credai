document.addEventListener('DOMContentLoaded', () => {
    // 1. Text Reveal Animation (Shutter Effect)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const textObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Optional: Stop observing once revealed
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Target elements with .reveal-text or .animate-on-scroll
    document.querySelectorAll('.reveal-on-scroll, .shutter-text span').forEach(el => {
        textObserver.observe(el);
    });

    // 2. Parallax Effect (Simple)
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroText = document.querySelector('.hero-bg-text');
        if (heroText) {
            heroText.style.transform = `translate(-50%, calc(-50% + ${scrolled * 0.2}px))`;
        }
    });
});
