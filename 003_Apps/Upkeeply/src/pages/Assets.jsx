import { useEffect, useState } from "react";

import { getAssets, updateAsset, deleteAsset } from "../lib/firestore";
import { useAuth } from "../contexts/AuthContext";
import { Package, MapPin, Tag, Edit2, Trash2, X, Save } from "lucide-react";
import clsx from "clsx";

export default function Assets() {
    const { currentUser } = useAuth();
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingAsset, setEditingAsset] = useState(null);

    async function fetchAssets() {
        if (currentUser) {
            try {
                const data = await getAssets(currentUser.uid);
                setAssets(data);
            } catch (error) {
                console.error("Error fetching assets:", error);
            } finally {
                setLoading(false);
            }
        }
    }

    useEffect(() => {
        fetchAssets();
    }, [currentUser]);

    const handleSaveEdit = async () => {
        if (!editingAsset) return;
        try {
            await updateAsset(currentUser.uid, editingAsset.id, editingAsset);
            setEditingAsset(null);
            fetchAssets();
        } catch (error) {
            console.error("Failed to update asset", error);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure you want to delete this asset?")) return;
        try {
            await deleteAsset(currentUser.uid, id);
            fetchAssets();
        } catch (error) {
            console.error("Failed to delete asset", error);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading assets...</div>;

    return (
        <div className="p-4 max-w-5xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">My Assets</h2>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
                    + Add Asset
                </button>
            </div>

            {assets.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl border border-dashed text-gray-500">
                    <Package className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>No assets tracked yet. Use the Chat to add one!</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {assets.map(asset => (
                        <div key={asset.id} className="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition-shadow relative group">
                            <div className="flex justify-between items-start mb-3">
                                <div className="bg-blue-50 text-blue-700 p-2 rounded-lg">
                                    <Package className="w-5 h-5" />
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={clsx("text-xs font-semibold px-2 py-1 rounded-full uppercase",
                                        asset.type === 'hvac' ? "bg-orange-100 text-orange-700" :
                                            asset.type === 'pool' ? "bg-cyan-100 text-cyan-700" :
                                                "bg-gray-100 text-gray-700"
                                    )}>
                                        {asset.type}
                                    </span>
                                    <button
                                        onClick={() => setEditingAsset(asset)}
                                        className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(asset.id)}
                                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <h3 className="font-bold text-lg text-gray-900 mb-1">{asset.name}</h3>

                            <div className="space-y-1">
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <MapPin className="w-4 h-4" /> {asset.location || "No location set"}
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <Tag className="w-4 h-4" /> {asset.manufacturer || "Unknown Make"} {asset.model}
                                </div>
                                {asset.notes && (
                                    <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded mt-2 italic">
                                        "{asset.notes}"
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Edit Modal */}
            {editingAsset && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-lg p-6 shadow-2xl">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold">Edit Asset</h3>
                            <button onClick={() => setEditingAsset(null)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Asset Name</label>
                                <input
                                    value={editingAsset.name}
                                    onChange={e => setEditingAsset({ ...editingAsset, name: e.target.value })}
                                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Make</label>
                                    <input
                                        value={editingAsset.manufacturer || ""}
                                        onChange={e => setEditingAsset({ ...editingAsset, manufacturer: e.target.value })}
                                        className="w-full border rounded-lg px-3 py-2 outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                                    <input
                                        value={editingAsset.model || ""}
                                        onChange={e => setEditingAsset({ ...editingAsset, model: e.target.value })}
                                        className="w-full border rounded-lg px-3 py-2 outline-none"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                                <input
                                    value={editingAsset.location || ""}
                                    onChange={e => setEditingAsset({ ...editingAsset, location: e.target.value })}
                                    className="w-full border rounded-lg px-3 py-2 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Notes / Specs</label>
                                <textarea
                                    value={editingAsset.notes || ""}
                                    onChange={e => setEditingAsset({ ...editingAsset, notes: e.target.value })}
                                    className="w-full border rounded-lg px-3 py-2 outline-none h-20 resize-none"
                                    placeholder="e.g. Filter size 20x20x1"
                                />
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                            <button
                                onClick={() => setEditingAsset(null)}
                                className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSaveEdit}
                                className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 flex items-center gap-2"
                            >
                                <Save className="w-4 h-4" /> Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
