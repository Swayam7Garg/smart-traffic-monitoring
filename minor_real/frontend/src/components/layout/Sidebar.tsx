
import { LayoutDashboard, Film, TrendingUp, Settings, AlertTriangle, Video, Activity } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SidebarProps {
  activePage: string;
  onPageChange: (page: string) => void;
}

const menuItems = [
  { id: 'dashboard', label: 'Live Monitor', icon: LayoutDashboard },
  { id: 'live', label: 'Video Analysis', icon: Film },
  { id: 'cameras', label: 'Cameras', icon: Video },
  { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  { id: 'emergency', label: 'Emergency', icon: AlertTriangle },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onPageChange }) => {
  return (
    <div className="w-64 glass h-screen fixed left-0 top-0 flex flex-col border-r border-slate-700/50">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold gradient-text">TrafficAI</h1>
            <p className="text-xs text-slate-400">Smart Monitoring</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-500/50'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/50'
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700/50">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600"></div>
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-200">System Active</p>
            <p className="text-xs text-slate-400">All systems operational</p>
          </div>
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        </div>
      </div>
    </div>
  );
};

