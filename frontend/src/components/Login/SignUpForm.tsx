import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/shared/utils";
import { useAuth } from "@/shared/auth";

const MANAGER_ROLES = [
  { value: "מנהל בוטיק", label: "מנהל בוטיק" },
  { value: "מנהל אזור", label: "מנהל אזור" },
  { value: "הנהלה בכירה", label: "הנהלה בכירה" },
] as const;

export function SignUpForm() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState(MANAGER_ROLES[0].value);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { signUp, isLoading } = useAuth();

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !name.trim() || !password || !confirmPassword) {
      setError("Please fill in all fields");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      await signUp({
        email: email.trim(),
        name: name.trim(),
        password,
        role,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
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
          <label className="text-sm font-medium text-[#B57A3A]">Full Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={cn(
              "w-full bg-transparent border-0 border-b border-[#D5C7B4]",
              "py-2 outline-none text-sm text-[#5B4A3A]"
            )}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#B57A3A]">Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className={cn(
              "w-full bg-transparent border-0 border-b border-[#D5C7B4]",
              "py-2 outline-none text-sm text-[#5B4A3A]"
            )}
          >
            {MANAGER_ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
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
              onClick={() => setShowPassword((prev) => !prev)}
              className={cn(
                "absolute inset-y-0 end-0",
                "inline-flex items-center justify-center ps-2 pe-0 text-[#B58B5A]"
              )}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          <p className="text-xs text-[#B58B5A]">
            Must be at least 6 characters
          </p>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-[#B57A3A]">Confirm Password</label>
          <div className="relative border-b border-[#D5C7B4]">
            <input
              type={showConfirmPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={cn(
                "w-full bg-transparent border-0 outline-none py-2 text-sm text-[#5B4A3A]"
              )}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword((prev) => !prev)}
              className={cn(
                "absolute inset-y-0 end-0",
                "inline-flex items-center justify-center ps-2 pe-0 text-[#B58B5A]"
              )}
              aria-label={showConfirmPassword ? "Hide password" : "Show password"}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
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
        {isLoading ? "Signing up..." : "Sign Up"}
      </button>
    </form>
  );
}

