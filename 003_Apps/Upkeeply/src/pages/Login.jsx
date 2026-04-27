import { useAuth } from "../contexts/AuthContext";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
    const { loginWithGoogle, currentUser } = useAuth();
    const [error, setError] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        if (currentUser) {
            navigate("/");
        }
    }, [currentUser, navigate]);

    const handleLogin = async () => {
        try {
            await loginWithGoogle();
        } catch (err) {
            console.error(err);
            setError("Failed to sign in. Please check your Firebase config.");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
                <h1 className="text-3xl font-bold text-blue-600 mb-2">Upkeeply</h1>
                <p className="text-gray-500 mb-8">Your smart home maintenance assistant</p>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
                        {error}
                    </div>
                )}

                <button
                    onClick={handleLogin}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors flex items-center justify-center gap-2"
                >
                    Sign in with Google (Demo Mode Available)
                </button>

                <p className="mt-6 text-xs text-gray-400">
                    If Firebase is not configured, this will enter Demo Mode.
                </p>
            </div>
        </div>
    );
}
