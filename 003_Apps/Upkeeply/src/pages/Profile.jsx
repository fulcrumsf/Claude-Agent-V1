import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { getProfile, saveProfile } from "../lib/firestore";
import { User, Phone, Mail, Save, Check } from "lucide-react";

export default function Profile() {
    const { currentUser } = useAuth();
    const [profile, setProfile] = useState({ phoneNumber: "", email: "" });
    const [loading, setLoading] = useState(true);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        if (currentUser) {
            getProfile(currentUser.uid).then(data => {
                setProfile({
                    email: data.email || currentUser.email || "",
                    phoneNumber: data.phoneNumber || ""
                });
                setLoading(false);
            });
        }
    }, [currentUser]);

    const handleSave = async () => {
        if (!currentUser) return;
        try {
            await saveProfile(currentUser.uid, profile);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (error) {
            console.error("Error saving profile:", error);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading profile...</div>;

    return (
        <div className="p-4 max-w-xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <User className="w-6 h-6" /> User Profile
            </h1>

            <div className="bg-white rounded-xl shadow-sm border p-6 space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <Mail className="w-4 h-4" /> Email Address
                    </label>
                    <input
                        type="email"
                        value={profile.email}
                        onChange={e => setProfile({ ...profile, email: e.target.value })}
                        className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="your@email.com"
                    />
                    <p className="text-xs text-gray-500 mt-1">Used for email notifications.</p>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <Phone className="w-4 h-4" /> Phone Number
                    </label>
                    <input
                        type="tel"
                        value={profile.phoneNumber}
                        onChange={e => setProfile({ ...profile, phoneNumber: e.target.value })}
                        className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="+1 (555) 000-0000"
                    />
                    <p className="text-xs text-gray-500 mt-1">Used for SMS text notifications.</p>
                </div>

                <div className="pt-4 border-t">
                    <button
                        onClick={handleSave}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                    >
                        {saved ? <Check className="w-5 h-5" /> : <Save className="w-5 h-5" />}
                        {saved ? "Saved Changes" : "Save Profile"}
                    </button>
                    {saved && <p className="text-center text-green-600 text-sm mt-2">Information updated successfully!</p>}
                </div>
            </div>
        </div>
    );
}
