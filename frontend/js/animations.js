document.addEventListener('DOMContentLoaded', () => {
    // Scroll Animation Observer
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Auto-add animation classes to common elements if they don't have them
    const cards = document.querySelectorAll('.feature-card, .footer-col, .step-item');
    cards.forEach((card, index) => {
        card.classList.add('animate-on-scroll');
        // Add staggered delays based on index (modulo 3 for simple grid staggering)
        const delay = (index % 3) * 100;
        card.style.transitionDelay = `${delay}ms`;
        observer.observe(card);
    });

    // Also observe any manually added .animate-on-scroll elements
    const manualElements = document.querySelectorAll('.animate-on-scroll');
    manualElements.forEach(el => observer.observe(el));

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
