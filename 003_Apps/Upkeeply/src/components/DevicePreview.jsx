import { useState } from 'react';
import { Smartphone, Tablet, Monitor } from 'lucide-react';
import clsx from 'clsx';

export default function DevicePreview({ children }) {
    const [device, setDevice] = useState('desktop'); // desktop, tablet, mobile

    return (
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
            <div className="bg-gray-800 p-2 rounded-xl mb-4 flex gap-2">
                <button
                    onClick={() => setDevice('mobile')}
                    className={clsx("p-2 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium",
                        device === 'mobile' ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
                    )}
                >
                    <Smartphone className="w-4 h-4" /> Mobile
                </button>
                <button
                    onClick={() => setDevice('tablet')}
                    className={clsx("p-2 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium",
                        device === 'tablet' ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
                    )}
                >
                    <Tablet className="w-4 h-4" /> Tablet
                </button>
                <button
                    onClick={() => setDevice('desktop')}
                    className={clsx("p-2 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium",
                        device === 'desktop' ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"
                    )}
                >
                    <Monitor className="w-4 h-4" /> Desktop
                </button>
            </div>

            <div
                className={clsx("bg-white transition-all duration-300 relative shadow-2xl overflow-hidden",
                    device === 'mobile' && "w-[375px] h-[667px] rounded-[30px] border-8 border-gray-800",
                    device === 'tablet' && "w-[768px] h-[1024px] rounded-[20px] border-8 border-gray-800",
                    device === 'desktop' && "w-full h-[calc(100vh-100px)] max-w-[1440px] rounded-xl border border-gray-700"
                )}
            >
                {children}
            </div>
            <p className="text-gray-500 text-xs mt-4">
                Note: In a real browser, responsive behavior depends on window size. This simulator forces container size.
            </p>
        </div>
    );
}
