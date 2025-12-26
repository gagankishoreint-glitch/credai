// Document Analyzer Logic

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadProgress = document.getElementById('uploadProgress');
const resultsCard = document.getElementById('resultsCard');

// Browse button click
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = 'var(--color-primary)';
    uploadZone.style.backgroundColor = 'rgba(0, 113, 227, 0.05)';
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.style.borderColor = '';
    uploadZone.style.backgroundColor = '';
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = '';
    uploadZone.style.backgroundColor = '';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    // Validate file
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF or image file (JPG, PNG)');
        return;
    }

    if (file.size > maxSize) {
        alert('File size must be less than 10MB');
        return;
    }

    // Show progress
    uploadProgress.style.display = 'block';
    uploadZone.style.display = 'none';

    // Simulate analysis (in real app, call backend API)
    setTimeout(() => {
        analyzeDocument(file);
    }, 2000);
}

function analyzeDocument(file) {
    // Mock analysis results
    const score = Math.floor(Math.random() * 30) + 65; // Random 65-95

    const findings = [
        { icon: '✅', text: 'Steady income pattern detected', positive: true },
        { icon: '✅', text: 'Low debt-to-income ratio (28%)', positive: true },
        { icon: '⚠️', text: 'Occasional overdrafts noted', positive: false },
        { icon: '✅', text: 'Good savings behavior', positive: true }
    ];

    const suggestions = [
        'Maintain current income consistency',
        'Avoid overdrafts to improve score further',
        'Consider increasing emergency savings to 6 months',
        'Set up automatic bill payments to avoid late fees'
    ];

    displayResults(score, findings, suggestions);
}

function displayResults(score, findings, suggestions) {
    // Hide progress, show results
    uploadProgress.style.display = 'none';
    resultsCard.style.display = 'block';

    // Display score
    document.getElementById('scoreValue').textContent = score;

    let scoreLabel = '';
    let scoreColor = '';

    if (score >= 80) {
        scoreLabel = 'Excellent Credit Strength';
        scoreColor = 'var(--color-success)';
    } else if (score >= 65) {
        scoreLabel = 'Good Credit Strength';
        scoreColor = 'var(--color-primary)';
    } else if (score >= 50) {
        scoreLabel = 'Fair Credit Strength';
        scoreColor = 'var(--color-warning)';
    } else {
        scoreLabel = 'Needs Improvement';
        scoreColor = 'var(--color-danger)';
    }

    document.getElementById('scoreLabel').textContent = scoreLabel;
    document.getElementById('scoreLabel').style.color = scoreColor;

    // Display findings
    const findingsHTML = findings.map(f => `
        <div class="finding-item">
            <span class="finding-icon">${f.icon}</span>
            <span>${f.text}</span>
        </div>
    `).join('');
    document.getElementById('findings').innerHTML = findingsHTML;

    // Display suggestions
    const suggestionsHTML = suggestions.map(s => `
        <div class="suggestion-item">
            <span class="suggestion-bullet">💡</span>
            <span>${s}</span>
        </div>
    `).join('');
    document.getElementById('suggestions').innerHTML = suggestionsHTML;

    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Analyze again button
document.getElementById('analyzeAgain').addEventListener('click', () => {
    resultsCard.style.display = 'none';
    uploadZone.style.display = 'block';
    fileInput.value = '';
});
