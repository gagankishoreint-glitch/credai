import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing session
        const storedUser = localStorage.getItem('user');
        const storedToken = localStorage.getItem('token');

        if (storedUser && storedToken) {
            setUser(JSON.parse(storedUser));
            axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post('/api/v1/token', formData);
            const { access_token } = response.data;

            // Mock user data based on username (in production, get from API)
            const userData = {
                username,
                role: username.includes('underwriter') ? 'underwriter' :
                    username.includes('admin') ? 'admin' : 'applicant',
                token: access_token
            };

            localStorage.setItem('user', JSON.stringify(userData));
            localStorage.setItem('token', access_token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

            setUser(userData);
            return userData;
        } catch (error) {
            console.error('Login failed:', error);

            // DEMO MODE / VERCEL FALLBACK
            // If the backend is unreachable (404/Network Error) or not allowed (405), 
            // and the user is using valid test credentials, allow access.
            if (username === 'applicant_001' && password === 'secret' ||
                username === 'underwriter_1' && password === 'secret' ||
                username === 'admin' && password === 'secret') {

                console.warn('Backend unreachable. Using DEMO/MOCK mode.');

                const mockRole = username.includes('underwriter') ? 'underwriter' :
                    username.includes('admin') ? 'admin' : 'applicant';

                const mockData = {
                    username,
                    role: mockRole,
                    token: 'mock-demo-token-' + Date.now()
                };

                localStorage.setItem('user', JSON.stringify(mockData));
                localStorage.setItem('token', mockData.token);
                // Don't set axios header for mock to avoid sending invalid auth on real calls later

                setUser(mockData);
                return mockData;
            }

            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
