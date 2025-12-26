// Currency Conversion Functionality

const currencyRates = {
    'INR': 1,
    'USD': 0.012,
    'EUR': 0.011,
    'GBP': 0.0095
};

const currencySymbols = {
    'INR': '₹',
    'USD': '$',
    'EUR': '€',
    'GBP': '£'
};

let currentCurrency = localStorage.getItem('currency') || 'INR';

// Initialize currency selector
document.addEventListener('DOMContentLoaded', function () {
    const currencySelector = document.getElementById('currencySelector');
    if (currencySelector) {
        currencySelector.value = currentCurrency;
        currencySelector.addEventListener('change', function (e) {
            currentCurrency = e.target.value;
            localStorage.setItem('currency', currentCurrency);
            updateCurrencyDisplay();
        });

        updateCurrencyDisplay();
    }
});

function updateCurrencyDisplay() {
    // Update all currency values on the page
    const currencyElements = document.querySelectorAll('[data-currency]');
    currencyElements.forEach(element => {
        const baseAmount = parseFloat(element.getAttribute('data-currency'));
        const convertedAmount = convertCurrency(baseAmount, 'INR', currentCurrency);
        element.textContent = formatCurrency(convertedAmount, currentCurrency);
    });
}

function convertCurrency(amount, from, to) {
    const inrAmount = amount / currencyRates[from];
    return inrAmount * currencyRates[to];
}

function formatCurrency(amount, currency) {
    const symbol = currencySymbols[currency];
    const formatted = new Intl.NumberFormat('en-IN').format(Math.round(amount));
    return `${symbol}${formatted}`;
}

// Export for use in other scripts
window.currencyUtils = {
    convert: convertCurrency,
    format: formatCurrency,
    getCurrentCurrency: () => currentCurrency,
    getSymbol: (currency) => currencySymbols[currency]
};
