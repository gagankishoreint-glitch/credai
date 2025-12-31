// Firebase Authentication Helper Functions
// Handles login, signup, logout, and auth state management

// Check if user is logged in
function checkAuth() {
    return new Promise((resolve, reject) => {
        auth.onAuthStateChanged((user) => {
            if (user) {
                resolve(user);
            } else {
                reject('Not authenticated');
            }
        });
    });
}

// Sign up new user
async function signUp(email, password, businessName) {
    try {
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        const user = userCredential.user;

        // Update user profile with business name
        await user.updateProfile({
            displayName: businessName
        });

        // Store additional user data in Firestore
        await db.collection('users').doc(user.uid).set({
            email: email,
            businessName: businessName,
            role: 'applicant',
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        console.log('✅ User registered:', user.email);
        return user;
    } catch (error) {
        console.error('❌ Signup error:', error);
        throw error;
    }
}

// Sign in existing user
async function signIn(email, password) {
    try {
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        const user = userCredential.user;

        console.log('✅ User logged in:', user.email);
        return user;
    } catch (error) {
        console.error('❌ Login error:', error);
        throw error;
    }
}

// Sign out user
async function signOut() {
    try {
        await auth.signOut();
        localStorage.clear();
        console.log('✅ User logged out');
        window.location.href = 'index.html';
    } catch (error) {
        console.error('❌ Logout error:', error);
        throw error;
    }
}

// Get current user
function getCurrentUser() {
    return auth.currentUser;
}

// Check if user is admin
async function isAdmin(userId) {
    try {
        const userDoc = await db.collection('users').doc(userId).get();
        if (userDoc.exists) {
            return userDoc.data().role === 'admin';
        }
        return false;
    } catch (error) {
        console.error('Error checking admin status:', error);
        return false;
    }
}

// Protect page - redirect to login if not authenticated
function protectPage(adminOnly = false) {
    auth.onAuthStateChanged(async (user) => {
        if (!user) {
            console.log('🔒 Not authenticated, redirecting to login...');
            window.location.href = 'login.html';
            return;
        }

        if (adminOnly) {
            const admin = await isAdmin(user.uid);
            if (!admin) {
                console.log('🔒 Not an admin, redirecting...');
                alert('Access denied. Admin privileges required.');
                window.location.href = 'dashboard.html';
            }
        }
    });
}

// Export functions to global scope
window.authHelpers = {
    checkAuth,
    signUp,
    signIn,
    signOut,
    getCurrentUser,
    isAdmin,
    protectPage
};
