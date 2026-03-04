import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/shared/utils";
import { useAuth } from "@/shared/auth";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  const togglePassword = () => {
    setShowPassword((prev) => !prev);
  };

  const handleForgotPasswordClick = () => {
    navigate("/forgot-password");
  };

  const handleSignUpClick = () => {
    navigate("/signup");
  };

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password) {
      setError("Please fill in all fields");
      return;
    }

    try {
      await login(email.trim(), password);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 text-start">
      {error && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#B57A3A]">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={cn(
              "w-full bg-transparent border-0 border-b border-[#D5C7B4]",
              "py-2 outline-none text-sm text-[#5B4A3A]"
            )}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#B57A3A]">Password</label>
          <div className="relative border-b border-[#D5C7B4]">
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={cn(
                "w-full bg-transparent border-0 outline-none py-2 text-sm text-[#5B4A3A]"
              )}
            />
            <button
              type="button"
              onClick={togglePassword}
              className={cn(
                "absolute inset-y-0 end-0",
                "inline-flex items-center justify-center ps-2 pe-0 text-[#B58B5A]"
              )}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs sm:text-sm text-[#B58B5A]">
        <button
          type="button"
          className="text-[#B58B5A]"
          onClick={handleForgotPasswordClick}
        >
          Forgot Password ?
        </button>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            className="h-3.5 w-3.5 rounded border border-[#D5C7B4] accent-[#B57A3A]"
          />
          <span>Remember Me</span>
        </label>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className={cn(
          "mt-2 w-full h-11 sm:h-12 rounded-md",
          "bg-[#262430] text-[#C49458]",
          "text-sm font-semibold tracking-wide",
          "shadow-md shadow-black/20",
          "disabled:opacity-50 disabled:cursor-not-allowed"
        )}
      >
        {isLoading ? "Logging in..." : "Log In"}
      </button>

      <div className="mt-10 text-center text-xs sm:text-sm text-[#B58B5A]">
        <span>Don&apos;t have an account ? </span>
        <button
          type="button"
          className="font-semibold text-[#B57A3A]"
          onClick={handleSignUpClick}
        >
          Sign Up
        </button>
      </div>
    </form>
  );
}

