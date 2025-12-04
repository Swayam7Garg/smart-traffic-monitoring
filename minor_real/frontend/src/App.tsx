import { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { DashboardPage } from './pages/Dashboard';
import { LiveMonitoring } from './pages/LiveMonitoring';
import Analytics from './pages/Analytics';
import Emergency from './pages/Emergency';
import Settings from './pages/Settings';
import CameraManagement from './pages/CameraManagement';

function App() {
  const [activePage, setActivePage] = useState('dashboard');

  const pageConfig = {
    dashboard: {
      title: 'Live Intersection Monitor',
      subtitle: '4-way real-time traffic monitoring and intelligent signal control',
    },
    live: {
      title: 'Video Analysis',
      subtitle: 'Upload and process traffic videos',
    },
    cameras: {
      title: 'Camera Management',
      subtitle: 'Manage traffic cameras and live streams',
    },
    analytics: {
      title: 'Analytics',
      subtitle: 'Traffic patterns and insights',
    },
    emergency: {
      title: 'Emergency Management',
      subtitle: 'Emergency vehicle priority system',
    },
    settings: {
      title: 'Settings',
      subtitle: 'System configuration and preferences',
    },
  };

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage />;
      case 'live':
        return <LiveMonitoring />;
      case 'cameras':
        return <CameraManagement />;
      case 'analytics':
        return <Analytics />;
      case 'emergency':
        return <Emergency />;
      case 'settings':
        return <Settings />;
      default:
        return <DashboardPage />;
    }
  };

  const currentPage = pageConfig[activePage as keyof typeof pageConfig];

  return (
    <div className="min-h-screen animated-gradient">
      {/* Sidebar */}
      <Sidebar activePage={activePage} onPageChange={setActivePage} />

      {/* Main Content */}
      <div className="ml-64">
        <Header title={currentPage.title} subtitle={currentPage.subtitle} />
        
        <main className="p-8">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default App;

