import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "@/App";
import { LoginPage, ForgotPasswordPage, SignUpPage } from "@/components";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<App />} />
      </Routes>
    </BrowserRouter>
  );
}

