// Theme Toggle Functionality
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const themeIcon = document.getElementById('theme-icon');

// Check for saved theme preference or default to 'dark'
const currentTheme = localStorage.getItem('theme') || 'dark';

// Set initial theme
html.setAttribute('data-theme', currentTheme);
updateThemeIcon(currentTheme);

// Theme toggle event listener
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

// Update theme icon based on current theme
function updateThemeIcon(theme) {
    if (themeIcon) {
        if (theme === 'dark') {
            // Sun icon for dark mode
            themeIcon.setAttribute('name', 'sunny-outline');
        } else {
            // Moon icon for light mode
            themeIcon.setAttribute('name', 'moon-outline');
        }
    }
}
