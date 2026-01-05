// Authentication Helper Functions (REST API Version)
// Replaces Firebase Auth with Custom Node.js/Postgres Auth using JWT

const API_BASE_URL = window.API_CONFIG ? window.API_CONFIG.BASE_URL : '/api';

// Check if user is logged in (Client side check of token)
function checkAuth() {
    return new Promise((resolve, reject) => {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');

        if (token && user) {
            resolve(JSON.parse(user));
        } else {
            reject('Not authenticated');
        }
    });
}

// Sign up new user
async function signUp(email, password, fullName) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, fullName })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Signup failed');
        }

        // Store Token & User
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));

        console.log('✅ User registered:', data.user.email);
        return data.user;
    } catch (error) {
        console.error('❌ Signup error:', error);
        throw error;
    }
}

// Sign in existing user
async function signIn(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Login failed');
        }

        // Store Token & User
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));

        console.log('✅ User logged in:', data.user.email);
        return data.user;
    } catch (error) {
        console.error('❌ Login error:', error);
        throw error;
    }
}

// Sign out user
function signOut() {
    localStorage.clear();
    console.log('✅ User logged out');
    window.location.href = 'index.html';
}

// Get current user
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

// Protect page - redirect to login if not authenticated
function protectPage(adminOnly = false) {
    const token = localStorage.getItem('token');
    if (!token) {
        console.log('🔒 Not authenticated, redirecting to login...');
        window.location.href = 'login.html';
        return;
    }

    // Optional: Validate token with backend if critical
}

// Export functions to global scope
window.authHelpers = {
    checkAuth,
    signUp,
    signIn,
    signOut,
    getCurrentUser,
    protectPage
};
