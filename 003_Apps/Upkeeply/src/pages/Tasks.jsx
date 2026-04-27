import { useEffect, useState } from "react";
import { getTasks, updateTaskStatus, updateTask } from "../lib/firestore";
import { useAuth } from "../contexts/AuthContext";
import { Calendar, CheckCircle2, AlertCircle, Edit2, X, Save } from "lucide-react";
import { format, isPast, isToday, parseISO } from "date-fns";
import clsx from "clsx";

export default function Tasks() {
    const { currentUser } = useAuth();
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingTask, setEditingTask] = useState(null);

    useEffect(() => {
        fetchTasks();
    }, [currentUser]);

    async function fetchTasks() {
        if (currentUser) {
            try {
                const data = await getTasks(currentUser.uid);
                setTasks(data);
            } catch (error) {
                console.error("Error fetching tasks:", error);
            } finally {
                setLoading(false);
            }
        }
    }

    const handleComplete = async (taskId) => {
        if (!confirm("Mark this task as completed?")) return;
        try {
            await updateTaskStatus(currentUser.uid, taskId, 'completed');
            fetchTasks(); // Refresh
        } catch (error) {
            console.error("Error updating task:", error);
        }
    };

    const handleSaveEdit = async () => {
        if (!editingTask) return;
        try {
            await updateTask(currentUser.uid, editingTask.id, editingTask);
            setEditingTask(null);
            fetchTasks();
        } catch (error) {
            console.error("Failed to update task", error);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading tasks...</div>;

    // Group tasks
    const dueTasks = tasks.filter(t => t.status !== 'completed');
    const completedTasks = tasks.filter(t => t.status === 'completed');

    return (
        <div className="p-4 max-w-3xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Maintenance Tasks</h2>
            </div>

            <div className="space-y-6">
                {/* Due / Upcoming */}
                <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Upcoming & Due</h3>
                    {dueTasks.length === 0 ? (
                        <p className="text-gray-400 italic">No pending tasks.</p>
                    ) : (
                        dueTasks.map(task => (
                            <div key={task.id} className="bg-white p-4 rounded-xl shadow-sm border flex items-center justify-between group hover:border-blue-300 transition-colors">
                                <div className="flex items-start gap-4">
                                    <button
                                        onClick={() => handleComplete(task.id)}
                                        className="mt-1 text-gray-300 hover:text-blue-600 transition-colors"
                                    >
                                        <CheckCircle2 className="w-6 h-6" />
                                    </button>
                                    <div>
                                        <h4 className="font-semibold text-gray-900">{task.title}</h4>
                                        <p className="text-sm text-gray-500 mb-1">{task.description}</p>

                                        <div className="flex items-center gap-4 text-xs font-medium">
                                            {task.dueDate && (
                                                <div className={clsx("flex items-center gap-1",
                                                    isPast(parseISO(task.dueDate)) && !isToday(parseISO(task.dueDate)) ? "text-red-600" :
                                                        isToday(parseISO(task.dueDate)) ? "text-orange-600" :
                                                            "text-gray-500"
                                                )}>
                                                    <Calendar className="w-3 h-3" />
                                                    {format(parseISO(task.dueDate), "MMM d, yyyy")}
                                                </div>
                                            )}
                                            {task.dueDate && isPast(parseISO(task.dueDate)) && !isToday(parseISO(task.dueDate)) && (
                                                <span className="text-red-600 bg-red-50 px-2 py-0.5 rounded flex items-center gap-1">
                                                    <AlertCircle className="w-3 h-3" /> Overdue
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setEditingTask(task)}
                                    className="p-2 text-gray-400 hover:text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <Edit2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))
                    )}
                </div>

                {/* Completed */}
                {completedTasks.length > 0 && (
                    <div className="space-y-3 opacity-60">
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Completed</h3>
                        {completedTasks.map(task => (
                            <div key={task.id} className="bg-gray-50 p-4 rounded-xl border flex items-center gap-4">
                                <div className="text-green-600">
                                    <CheckCircle2 className="w-5 h-5" />
                                </div>
                                <div>
                                    <h4 className="font-medium text-gray-700 line-through">{task.title}</h4>
                                    <p className="text-xs text-gray-500">Completed on {task.lastCompletedAt?.toDate ? format(task.lastCompletedAt.toDate(), "MMM d") : "Recently"}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Edit Modal */}
            {editingTask && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-2xl w-full max-w-lg p-6 shadow-2xl">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold">Edit Task</h3>
                            <button onClick={() => setEditingTask(null)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Task Title</label>
                                <input
                                    value={editingTask.title}
                                    onChange={e => setEditingTask({ ...editingTask, title: e.target.value })}
                                    className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea
                                    value={editingTask.description || ""}
                                    onChange={e => setEditingTask({ ...editingTask, description: e.target.value })}
                                    className="w-full border rounded-lg px-3 py-2 outline-none h-20 resize-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                                <input
                                    type="date"
                                    value={editingTask.dueDate || ""}
                                    onChange={e => setEditingTask({ ...editingTask, dueDate: e.target.value })}
                                    className="w-full border rounded-lg px-3 py-2 outline-none"
                                />
                            </div>

                            <div className="pt-2">
                                <label className="block text-sm font-medium text-gray-700 mb-2">Notification Preferences</label>
                                <div className="flex gap-4">
                                    <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={editingTask.notifications?.email || false}
                                            onChange={() => setEditingTask({
                                                ...editingTask,
                                                notifications: { ...editingTask.notifications, email: !editingTask.notifications?.email }
                                            })}
                                            className="rounded text-blue-600"
                                        /> Email
                                    </label>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={editingTask.notifications?.text || false}
                                            onChange={() => setEditingTask({
                                                ...editingTask,
                                                notifications: { ...editingTask.notifications, text: !editingTask.notifications?.text }
                                            })}
                                            className="rounded text-blue-600"
                                        /> Text
                                    </label>
                                    <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={editingTask.notifications?.calendar || false}
                                            onChange={() => setEditingTask({
                                                ...editingTask,
                                                notifications: { ...editingTask.notifications, calendar: !editingTask.notifications?.calendar }
                                            })}
                                            className="rounded text-blue-600"
                                        /> Google Calendar
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                            <button
                                onClick={() => setEditingTask(null)}
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
