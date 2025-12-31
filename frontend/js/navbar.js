document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar');
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

    // Sticky Navbar on Scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            navbar.classList.add('is-sticky');
        } else {
            navbar.classList.remove('is-sticky');
        }
    });

    // Dropdown Logic
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const parent = toggle.closest('.dropdown');

            // Close others
            document.querySelectorAll('.dropdown.is-active').forEach(d => {
                if (d !== parent) d.classList.remove('is-active');
            });

            // Toggle current
            parent.classList.toggle('is-active');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown.is-active').forEach(d => {
                d.classList.remove('is-active');
            });
        }
    });
});
