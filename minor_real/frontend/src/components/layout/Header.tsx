
import { Bell, Search, User } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="glass border-b border-slate-700/50 px-8 py-4 mb-6 sticky top-0 z-10">
      <div className="flex items-center justify-between">
        {/* Title */}
        <div>
          <h1 className="text-2xl font-bold text-slate-100">{title}</h1>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
            />
          </div>

          {/* Notifications */}
          <button className="relative p-2 hover:bg-slate-700/50 rounded-lg transition-colors">
            <Bell className="w-5 h-5 text-slate-300" />
            <Badge
              variant="danger"
              className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center text-xs"
            >
              3
            </Badge>
          </button>

          {/* Profile */}
          <button className="flex items-center gap-3 px-3 py-2 hover:bg-slate-700/50 rounded-lg transition-colors">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium text-slate-200">Admin</p>
              <p className="text-xs text-slate-400">Administrator</p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
};

