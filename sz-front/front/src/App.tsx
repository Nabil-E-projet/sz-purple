import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Homepage from "./pages/Homepage";
import LoginPage from "./pages/LoginPage";
import UploadPage from "./pages/UploadPage";
import Dashboard from "./pages/Dashboard";
import AnalysisDetails from "./pages/AnalysisDetails";
import NotFound from "./pages/NotFound";
import BuyCredits from "./pages/BuyCredits";
import PaymentSuccess from "./pages/PaymentSuccess";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import WelcomeAnimation from "./components/WelcomeAnimation";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <WelcomeAnimation />
      <BrowserRouter>
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<PaymentSuccess />} />
                <Route path="/home" element={<Homepage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/upload"
                  element={
                    <ProtectedRoute>
                      <UploadPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/buy-credits"
                  element={
                    <ProtectedRoute>
                      <BuyCredits />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analysis/:id"
                  element={
                    <ProtectedRoute>
                      <AnalysisDetails />
                    </ProtectedRoute>
                  }
                />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
