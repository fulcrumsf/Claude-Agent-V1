import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { MessageSquare, ClipboardList, Package, LogOut, Menu, User } from "lucide-react";
import clsx from 'clsx';
import { useAuth } from "../contexts/AuthContext";

function NavItem({ to, icon: Icon, label }) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                clsx(
                    "flex flex-col items-center justify-center p-2 rounded-lg transition-colors",
                    isActive ? "text-blue-600 bg-blue-50" : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                )
            }
        >
            <Icon className="w-6 h-6" />
            <span className="text-xs mt-1 font-medium">{label}</span>
        </NavLink>
    );
}

export default function Layout() {
    return (
        <div className="flex h-full bg-gray-100">
            {/* Desktop Sidebar */}
            <aside className="hidden md:flex flex-col w-64 bg-white border-r px-4 py-6">
                <h1 className="text-2xl font-bold text-blue-600 mb-8 px-2">Upkeeply</h1>
                <nav className="space-y-2">
                    <NavLink
                        to="/"
                        className={({ isActive }) =>
                            clsx("flex items-center gap-3 px-3 py-2 rounded-lg font-medium",
                                isActive ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-50")
                        }
                    >
                        <MessageSquare className="w-5 h-5" />
                        Chat
                    </NavLink>
                    <NavLink
                        to="/tasks"
                        className={({ isActive }) =>
                            clsx("flex items-center gap-3 px-3 py-2 rounded-lg font-medium",
                                isActive ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-50")
                        }
                    >
                        <CheckSquare className="w-5 h-5" />
                        Tasks
                    </NavLink>
                    <NavLink
                        to="/assets"
                        className={({ isActive }) =>
                            clsx("flex items-center gap-3 px-3 py-2 rounded-lg font-medium",
                                isActive ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-50")
                        }
                    >
                        <Package className="w-5 h-5" />
                        Assets
                    </NavLink>
                </nav>

                <div className="mt-auto">
                    <div className="flex items-center gap-3 px-3 py-2 text-gray-600">
                        <User className="w-5 h-5" />
                        <span className="text-sm font-medium">User Profile</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto relative">
                <Outlet />
            </main>

            {/* Mobile Bottom Nav */}
            <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around p-2 pb-safe">
                <NavItem to="/" icon={MessageSquare} label="Chat" />
                <NavItem to="/tasks" icon={CheckSquare} label="Tasks" />
                <NavItem to="/assets" icon={Package} label="Assets" />
                <NavItem to="/profile" icon={User} label="Profile" />
            </nav>
        </div>
    );
}
