document.addEventListener('DOMContentLoaded', () => {

    // 1. Custom Cursor Logic
    const cursorDot = document.querySelector('.cursor-dot');
    const cursorCircle = document.querySelector('.cursor-circle');

    // Initial hiding until mouse moves
    cursorDot.style.opacity = '0';
    cursorCircle.style.opacity = '0';

    document.addEventListener('mousemove', (e) => {
        const posX = e.clientX;
        const posY = e.clientY;

        // Move dot instantly
        cursorDot.style.left = `${posX}px`;
        cursorDot.style.top = `${posY}px`;
        cursorDot.style.opacity = '1';

        // Move circle with slight delay (handled by CSS transition usually, but let's ensure it follows)
        // With CSS transitions on left/top, we just set the coordinates.
        cursorCircle.style.left = `${posX}px`;
        cursorCircle.style.top = `${posY}px`;
        cursorCircle.style.opacity = '1';
    });

    // Hover interactions for cursor
    const interactiveElements = document.querySelectorAll('a, button, .list-row, .grid-item');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            document.body.classList.add('hovering');
        });
        el.addEventListener('mouseleave', () => {
            document.body.classList.remove('hovering');
        });
    });

    // 2. Scroll Reveal (Intersection Observer)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px'
    };

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Optional: trigger child animations if needed
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal-up, .hero-meta').forEach(el => {
        scrollObserver.observe(el);
    });

    // 3. Smooth Anchor Scrolling (Tab Selection Movement)
    document.querySelectorAll('.nav-links a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetDiv = document.getElementById(targetId);
            if (targetDiv) {
                targetDiv.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
            // Update active state
            document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active-link'));
            this.classList.add('active-link');
        });
    });
});
