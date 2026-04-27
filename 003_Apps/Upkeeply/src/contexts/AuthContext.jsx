import { createContext, useContext, useEffect, useState } from "react";
import { onAuthStateChanged, signInWithPopup, GoogleAuthProvider, signOut } from "firebase/auth";
import { auth } from "../lib/firebase";

const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if we have valid config (naive check) or if we want to force mock
        const isMock = !auth.app.options.apiKey || auth.app.options.apiKey === "YOUR_API_KEY";

        if (isMock) {
            console.log("Firebase not configured. Using Mock Auth.");
            setLoading(false);
            return;
        }

        const unsubscribe = onAuthStateChanged(auth, (user) => {
            setCurrentUser(user);
            setLoading(false);
        });

        return unsubscribe;
    }, []);

    const loginWithGoogle = async () => {
        // Check for mock mode
        if (!auth.app.options.apiKey || auth.app.options.apiKey === "YOUR_API_KEY") {
            const mockUser = {
                uid: "mock-user-123",
                displayName: "Demo User",
                email: "demo@upkeeply.com",
                photoURL: null
            };
            setCurrentUser(mockUser);
            return;
        }
        const provider = new GoogleAuthProvider();
        return signInWithPopup(auth, provider);
    };

    const logout = () => {
        if (!auth.app.options.apiKey || auth.app.options.apiKey === "YOUR_API_KEY") {
            setCurrentUser(null);
            return Promise.resolve();
        }
        return signOut(auth);
    };

    const value = {
        currentUser,
        loginWithGoogle,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
