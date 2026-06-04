import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import LoginPage from '@/features/auth/LoginPage';
import ChannelAnalyzerPage from '@/features/channels/ChannelAnalyzerPage';
import DashboardPage from '@/features/dashboard/DashboardPage';
import KeywordExplorerPage from '@/features/keywords/KeywordExplorerPage';
import ReportsPage from '@/features/reports/ReportsPage';
import TrendExplorerPage from '@/features/trends/TrendExplorerPage';
import { useAuthStore } from '@/stores/authStore';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="trends" element={<TrendExplorerPage />} />
        <Route path="channels" element={<ChannelAnalyzerPage />} />
        <Route path="keywords" element={<KeywordExplorerPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="reports/:id" element={<ReportsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
