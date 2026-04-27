import { useState, useRef, useEffect } from "react";
import { Send, Image, Plus, Check, RotateCcw } from "lucide-react";
import { generateActionFromInput } from "../lib/gemini";
import { getAssets, createAsset, createTask, getProfile } from "../lib/firestore";
import { useAuth } from "../contexts/AuthContext";
import { addDays, format } from "date-fns";
import { useNavigate } from "react-router-dom";

export default function Chat() {
    const { currentUser } = useAuth();
    const navigate = useNavigate();
    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem("upkeeply_chat_history");
        return saved ? JSON.parse(saved) : [
            { role: "system", text: "Hello! I can help you track your home assets and maintenance tasks. Upload a photo or describe an update." }
        ];
    });
    const [inputText, setInputText] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [selectedImage, setSelectedImage] = useState(null);
    const [existingAssets, setExistingAssets] = useState([]);
    const [userProfile, setUserProfile] = useState({});
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (currentUser) {
            getAssets(currentUser.uid).then(setExistingAssets);
            getProfile(currentUser.uid).then(setUserProfile);
        }
    }, [currentUser]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // ... handleImageSelect, updateMessageState, handleFrequencySelect, toggleNotification ...

    // ... handleSend ...

    const handleConfirmAction = async (actionData, messageIndex) => {
        if (!currentUser) {
            alert("Please sign in to save data.");
            return;
        }

        // VALIDATION: Check for missing contact info
        const notifs = actionData.notifications || {};
        if (notifs.email && !userProfile.email && !currentUser.email) {
            if (confirm("I don't have an email on file for you. Would you like to add one in your Profile?")) {
                navigate("/profile");
                return;
            }
        }
        if (notifs.text && !userProfile.phoneNumber) {
            if (confirm("I don't have a phone number on file for you. Would you like to add one in your Profile?")) {
                navigate("/profile");
                return;
            }
        }

        try {
            let assetId = actionData.asset?.id; // Check if AI suggested an existing ID

            if (actionData.asset && !assetId) {
                // Create new only if no ID returned
                assetId = await createAsset(currentUser.uid, actionData.asset);
                // Refresh local asset list
                const updated = await getAssets(currentUser.uid);
                setExistingAssets(updated);
            }

            if (actionData.task) {
                const taskPayload = {
                    ...actionData.task,
                    assetId,
                    notifications: notifs // INCLUDE NOTIFICATIONS
                };
                await createTask(currentUser.uid, taskPayload);
            }

            // Update message to show confirmed
            setMessages(prev => prev.map((msg, idx) =>
                idx === messageIndex ? { ...msg, confirmed: true } : msg
            ));

        } catch (error) {
            console.error("Error saving:", error);
            alert("Failed to save data.");
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <div className="p-4 bg-white border-b flex justify-between items-center shadow-sm">
                <h1 className="font-semibold text-gray-800">Maintenance Assistant</h1>
                <button
                    onClick={() => {
                        if (confirm("Start a new chat? This will clear current history.")) {
                            setMessages([{ role: "system", text: "Hello! I can help you track your home assets and maintenance tasks. Upload a photo or describe an update." }]);
                        }
                    }}
                    className="text-gray-500 hover:text-blue-600 transition-colors flex items-center gap-1 text-sm font-medium"
                >
                    <RotateCcw className="w-4 h-4" /> New Chat
                </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        <div className={`max-w-[85%] md:max-w-md p-4 rounded-2xl ${msg.role === "user"
                            ? "bg-blue-600 text-white rounded-br-none"
                            : "bg-white border shadow-sm text-gray-800 rounded-bl-none"
                            }`}>
                            <p className="whitespace-pre-wrap">{msg.text}</p>
                            {msg.image && (
                                <img src={msg.image} alt="User upload" className="mt-2 rounded-lg max-h-48 border border-white/20" />
                            )}

                            {msg.actionData && !msg.confirmed && (
                                <div className="mt-4 bg-gray-50 rounded-xl p-3 border text-sm">
                                    <div className="font-semibold text-gray-700 mb-2">Proposed Action</div>
                                    {msg.actionData.asset && (
                                        <div className="mb-2 bg-white p-2 rounded border">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className={`badge px-2 py-0.5 rounded text-xs font-medium ${msg.actionData.asset.id ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                                                    {msg.actionData.asset.id ? 'UPDATE ITEM' : 'NEW ITEM'}
                                                </span>
                                                <span className="font-bold text-gray-800">{msg.actionData.asset.name}</span>
                                            </div>
                                            {/* Details View */}
                                            <div className="text-xs text-gray-600 space-y-1 pl-1">
                                                {msg.actionData.asset.location && <div>📍 {msg.actionData.asset.location}</div>}
                                                {msg.actionData.asset.manufacturer && <div>🏭 {msg.actionData.asset.manufacturer}</div>}
                                                {msg.actionData.asset.model && <div>🔢 Model: {msg.actionData.asset.model}</div>}
                                                {msg.actionData.asset.notes && <div className="italic text-gray-500">"{msg.actionData.asset.notes}"</div>}
                                            </div>
                                        </div>
                                    )}
                                    {msg.actionData.task && (
                                        <div className="mb-2">
                                            <span className="badge bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-xs font-medium mr-2">NEW TASK</span>
                                            <span className="font-medium">{msg.actionData.task.title}</span>

                                            {/* Frequency Buttons */}
                                            {msg.actionData.frequencyOptions && msg.actionData.frequencyOptions.length > 0 ? (
                                                <div className="mt-2 space-y-1">
                                                    <p className="text-xs text-gray-500 font-medium">When should I remind you?</p>
                                                    <div className="flex flex-wrap gap-2">
                                                        {msg.actionData.frequencyOptions.map((opt, i) => (
                                                            <button
                                                                key={i}
                                                                onClick={() => handleFrequencySelect(idx, opt)}
                                                                className="px-3 py-1 bg-white border border-blue-200 text-blue-700 text-xs rounded-full hover:bg-blue-50 transition-colors"
                                                            >
                                                                {opt.label}
                                                            </button>
                                                        ))}
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="text-gray-500 text-xs mt-1 font-medium">
                                                    Due: {msg.actionData.task.dueDate || "No date set"}
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Notification Toggles (Only show if task exists) */}
                                    {msg.actionData.task && (
                                        <div className="mt-3 py-2 border-t border-gray-100">
                                            <p className="text-xs text-gray-500 font-medium mb-2">Notify me via:</p>
                                            <div className="flex gap-3">
                                                <label className="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
                                                    <input
                                                        type="checkbox"
                                                        checked={msg.actionData.notifications?.email || false}
                                                        onChange={() => toggleNotification(idx, 'email')}
                                                        className="rounded text-blue-600 focus:ring-blue-500"
                                                    /> Email
                                                </label>
                                                <label className="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
                                                    <input
                                                        type="checkbox"
                                                        checked={msg.actionData.notifications?.text || false}
                                                        onChange={() => toggleNotification(idx, 'text')}
                                                        className="rounded text-blue-600 focus:ring-blue-500"
                                                    /> Text
                                                </label>
                                                <label className="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
                                                    <input
                                                        type="checkbox"
                                                        checked={msg.actionData.notifications?.calendar || false}
                                                        onChange={() => toggleNotification(idx, 'calendar')}
                                                        className="rounded text-blue-600 focus:ring-blue-500"
                                                    /> Calendar
                                                </label>
                                            </div>
                                        </div>
                                    )}

                                    {/* Confirm Button - Hide if waiting for frequency selection */}
                                    {(!msg.actionData.frequencyOptions || msg.actionData.frequencyOptions.length === 0) && (
                                        <button
                                            onClick={() => handleConfirmAction(msg.actionData, idx)}
                                            className="mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
                                        >
                                            <Check className="w-4 h-4" /> Confirm & Save
                                        </button>
                                    )}
                                </div>
                            )}

                            {msg.actionData && msg.actionData.amazonSuggestions && (
                                <div className="mt-3 grid grid-cols-2 gap-2">
                                    {msg.actionData.amazonSuggestions.map((product, pIdx) => (
                                        <a href="#" key={pIdx} className="block bg-white p-2 rounded-lg border hover:shadow-md transition-shadow no-underline">
                                            <div className="w-full h-20 bg-gray-100 rounded mb-2 flex items-center justify-center text-xs text-gray-400">Product Image</div>
                                            <div className="text-xs font-medium text-gray-800 line-clamp-2 leading-tight">{product.title}</div>
                                            <div className="text-xs font-bold text-orange-600 mt-1">{product.price}</div>
                                        </a>
                                    ))}
                                </div>
                            )}

                            {msg.confirmed && (
                                <div className="mt-2 text-xs text-green-600 font-medium flex items-center gap-1">
                                    <Check className="w-3 h-3" /> Saved successfully
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="flex justify-start">
                        <div className="bg-white border shadow-sm p-4 rounded-2xl rounded-bl-none flex items-center gap-2">
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t">
                <div className="max-w-3xl mx-auto flex items-center gap-3">
                    <div className="relative">
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="p-2 text-gray-400 hover:text-blue-600 transition-colors bg-gray-100 rounded-full"
                        >
                            <Image className="w-5 h-5" />
                        </button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleImageSelect}
                            accept="image/*"
                            className="hidden"
                        />
                        {selectedImage && (
                            <div className="absolute bottom-full mb-2 left-0 w-16 h-16 bg-gray-100 rounded-lg border overflow-hidden">
                                <img src={selectedImage} alt="Preview" className="w-full h-full object-cover" />
                                <button
                                    onClick={() => setSelectedImage(null)}
                                    className="absolute top-0 right-0 bg-red-500 text-white p-0.5 rounded-bl"
                                >
                                    <Plus className="w-3 h-3 rotate-45" />
                                </button>
                            </div>
                        )}
                    </div>
                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type a message..."
                        className="flex-1 bg-gray-100 rounded-full px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all font-medium"
                    />
                    <button
                        onClick={handleSend}
                        disabled={(!inputText.trim() && !selectedImage) || isTyping}
                        className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
