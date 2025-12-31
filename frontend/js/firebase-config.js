// Firebase Configuration
// Replace these with your actual Firebase project credentials
// Get these from: https://console.firebase.google.com/project/YOUR_PROJECT/settings/general

const firebaseConfig = {
    apiKey: "AIzaSyATHFi-xBm_J2qXeV7hzI2RxjyFPi_vi5M",
    authDomain: "creda-e8c01.firebaseapp.com",
    projectId: "creda-e8c01",
    storageBucket: "creda-e8c01.firebasestorage.app",
    messagingSenderId: "850357811532",
    appId: "1:850357811532:web:9ebe3c0185be8a6f82b7e9"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firestore
const db = firebase.firestore();

// Initialize Auth
const auth = firebase.auth();

// Export for use in other files
window.db = db;
window.auth = auth;
window.firebase = firebase;

console.log('Firebase initialized successfully!');
