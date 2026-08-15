import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Scanner from "./pages/Scanner";
import ScanResult from "./pages/ScanResult";
import History from "./pages/History";
import Statistics from "./pages/Statistics";
import Privacy from "./pages/Privacy";
import Settings from "./pages/Settings";
import Advisor from "./pages/Advisor";
import NotFound from "./pages/NotFound";
import { useAuth } from "./context/AuthContext";

function AdaptiveLayout() {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return <div className="min-h-screen grid place-items-center text-slate-400">Loading...</div>;
  }
  return isAuthenticated ? <AppLayout /> : <PublicLayout />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicLayout />}>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Route>
          <Route element={<AdaptiveLayout />}>
            <Route path="/scan-result" element={<ScanResult />} />
          </Route>
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/scanner" element={<Scanner />} />
            <Route path="/history" element={<History />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/advisor" element={<Advisor />} />
          </Route>
          <Route path="/home" element={<Navigate to="/" replace />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
