import { useState } from "react";
import { X, Eye, EyeOff } from "lucide-react";
import { cn } from "@/shared/utils";
import { useAuth } from "@/shared/auth";

interface LoginModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function LoginModal({ onClose, onSuccess }: LoginModalProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, isLoading } = useAuth();

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password) {
      setError("נא למלא את כל השדות");
      return;
    }

    try {
      await login(email.trim(), password);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "ההתחברות נכשלה");
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className={cn(
          "relative w-[90vw] max-w-md",
          "bg-[#F9F3E8] rounded-2xl",
          "border border-primary-300/70",
          "shadow-xl",
          "p-8"
        )}
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 end-4 p-1.5 rounded-full text-primary-800/60 hover:text-primary-800 hover:bg-primary-200/40 transition-colors"
          aria-label="סגור"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="text-center mb-6">
          <img
            src="/assets/nespresso-logo.png"
            alt="Nespresso"
            className="h-5 mx-auto mb-4 opacity-70"
          />
          <h2 className="text-xl font-semibold text-primary-900">
            התחברו כדי להמשיך
          </h2>
          <p className="text-sm text-primary-800/70 mt-1">
            נבנה את סידור העבודה שלכם
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {error && (
            <div className="rounded-lg bg-red-50/80 border border-red-200/60 px-3 py-2 text-sm text-red-600">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-primary-700">
              אימייל
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              dir="ltr"
              className={cn(
                "w-full bg-white/60 rounded-lg",
                "border border-primary-300/50",
                "px-3 py-2.5 outline-none text-sm text-primary-900",
                "focus:border-primary-500 transition-colors"
              )}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-primary-700">
              סיסמה
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                dir="ltr"
                className={cn(
                  "w-full bg-white/60 rounded-lg",
                  "border border-primary-300/50",
                  "px-3 py-2.5 pe-10 outline-none text-sm text-primary-900",
                  "focus:border-primary-500 transition-colors"
                )}
              />
              <button
                type="button"
                onClick={() => setShowPassword((p) => !p)}
                className="absolute inset-y-0 end-0 flex items-center pe-3 text-primary-400"
                aria-label={showPassword ? "הסתר סיסמה" : "הצג סיסמה"}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={cn(
              "w-full h-11 rounded-lg mt-1",
              "bg-primary-950 text-primary-500",
              "text-sm font-semibold tracking-wide",
              "shadow-md shadow-black/20",
              "hover:bg-primary-900 transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            {isLoading ? "מתחבר..." : "התחברות"}
          </button>

          <p className="text-center text-xs text-primary-800/60 mt-1">
            אין לכם חשבון?{" "}
            <a href="/signup" className="font-semibold text-primary-700 hover:text-primary-600">
              הרשמה
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
