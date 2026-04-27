import { db } from "./firebase";
import { collection, addDoc, updateDoc, deleteDoc, doc, query, where, getDocs, getDoc, setDoc, orderBy, serverTimestamp } from "firebase/firestore";
import { v4 as uuidv4 } from 'uuid';

// Helper to check if we are in mock mode (invalid config)
const runWithFallback = async (operation, mockOperation) => {
    try {
        if (!db.app.options.apiKey || db.app.options.apiKey === "YOUR_API_KEY") throw new Error("Mock Mode");
        return await operation();
    } catch (err) {
        console.warn("Firestore operation failed or in Mock Mode, using LocalStorage:", err.message);
        return mockOperation();
    }
};



// --- Profile ---

export async function getProfile(userId) {
    return runWithFallback(
        async () => {
            const docRef = doc(db, "users", userId, "profile", "main");
            const profileDoc = await getDoc(docRef);
            return profileDoc.exists() ? profileDoc.data() : {};
        },
        async () => {
            return JSON.parse(localStorage.getItem(`upkeeply_profile_${userId}`) || "{}");
        }
    );
}

export async function saveProfile(userId, profileData) {
    return runWithFallback(
        async () => {
            const docRef = doc(db, "users", userId, "profile", "main");
            await setDoc(docRef, profileData, { merge: true });
        },
        async () => {
            const current = JSON.parse(localStorage.getItem(`upkeeply_profile_${userId}`) || "{}");
            localStorage.setItem(`upkeeply_profile_${userId}`, JSON.stringify({ ...current, ...profileData }));
        }
    );
}



// --- Assets ---

export async function createAsset(userId, assetData) {
    return runWithFallback(
        async () => {
            const assetsRef = collection(db, "users", userId, "assets");
            const docRef = await addDoc(assetsRef, {
                ...assetData,
                createdAt: serverTimestamp()
            });
            return docRef.id;
        },
        async () => {
            const assets = JSON.parse(localStorage.getItem(`upkeeply_assets_${userId}`) || "[]");
            const newAsset = { ...assetData, id: uuidv4(), createdAt: new Date().toISOString(), userId };
            assets.unshift(newAsset);
            localStorage.setItem(`upkeeply_assets_${userId}`, JSON.stringify(assets));
            return newAsset.id;
        }
    );
}

export async function getAssets(userId) {
    return runWithFallback(
        async () => {
            const assetsRef = collection(db, "users", userId, "assets");
            const q = query(assetsRef, orderBy("createdAt", "desc"));
            const snapshot = await getDocs(q);
            return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        },
        async () => {
            return JSON.parse(localStorage.getItem(`upkeeply_assets_${userId}`) || "[]");
        }
    );
}

export async function updateAsset(userId, assetId, updates) {
    return runWithFallback(
        async () => {
            const assetRef = doc(db, "users", userId, "assets", assetId);
            await updateDoc(assetRef, updates);
        },
        async () => {
            const assets = JSON.parse(localStorage.getItem(`upkeeply_assets_${userId}`) || "[]");
            const updated = assets.map(a => a.id === assetId ? { ...a, ...updates } : a);
            localStorage.setItem(`upkeeply_assets_${userId}`, JSON.stringify(updated));
        }
    );
}

export async function deleteAsset(userId, assetId) {
    return runWithFallback(
        async () => {
            const assetRef = doc(db, "users", userId, "assets", assetId);
            await deleteDoc(assetRef);
        },
        async () => {
            const assets = JSON.parse(localStorage.getItem(`upkeeply_assets_${userId}`) || "[]");
            const filtered = assets.filter(a => a.id !== assetId);
            localStorage.setItem(`upkeeply_assets_${userId}`, JSON.stringify(filtered));
        }
    );
}

// --- Tasks ---

export async function createTask(userId, taskData) {
    return runWithFallback(
        async () => {
            const tasksRef = collection(db, "users", userId, "tasks");
            const docRef = await addDoc(tasksRef, {
                ...taskData,
                createdAt: serverTimestamp(),
                status: "upcoming" // default
            });
            return docRef.id;
        },
        async () => {
            const tasks = JSON.parse(localStorage.getItem(`upkeeply_tasks_${userId}`) || "[]");
            const newTask = { ...taskData, id: uuidv4(), createdAt: new Date().toISOString(), status: "upcoming", userId };
            tasks.push(newTask);
            localStorage.setItem(`upkeeply_tasks_${userId}`, JSON.stringify(tasks));
            return newTask.id;
        }
    );
}

export async function getTasks(userId) {
    return runWithFallback(
        async () => {
            const tasksRef = collection(db, "users", userId, "tasks");
            // Simple query for MVP, ideally compound queries for status
            const q = query(tasksRef, orderBy("dueDate", "asc"));
            const snapshot = await getDocs(q);
            return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        },
        async () => {
            const tasks = JSON.parse(localStorage.getItem(`upkeeply_tasks_${userId}`) || "[]");
            // Sort locally
            return tasks.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
        }
    );
}

export async function updateTask(userId, taskId, updates) {
    return runWithFallback(
        async () => {
            const taskRef = doc(db, "users", userId, "tasks", taskId);
            await updateDoc(taskRef, updates);
        },
        async () => {
            const tasks = JSON.parse(localStorage.getItem(`upkeeply_tasks_${userId}`) || "[]");
            const updatedTasks = tasks.map(t => t.id === taskId ? { ...t, ...updates } : t);
            localStorage.setItem(`upkeeply_tasks_${userId}`, JSON.stringify(updatedTasks));
        }
    );
}

export async function updateTaskStatus(userId, taskId, status) {
    return runWithFallback(
        async () => {
            const taskRef = doc(db, "users", userId, "tasks", taskId);
            await updateDoc(taskRef, {
                status,
                lastCompletedAt: status === 'completed' ? serverTimestamp() : null
            });
        },
        async () => {
            const tasks = JSON.parse(localStorage.getItem(`upkeeply_tasks_${userId}`) || "[]");
            const updatedTasks = tasks.map(t => {
                if (t.id === taskId) {
                    return {
                        ...t,
                        status,
                        lastCompletedAt: status === 'completed' ? new Date().toISOString() : null
                    };
                }
                return t;
            });
            localStorage.setItem(`upkeeply_tasks_${userId}`, JSON.stringify(updatedTasks));
        }
    );
}


// Helper to check if we are in mock mode (invalid config)
