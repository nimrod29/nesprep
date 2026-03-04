import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/shared/utils";

export function SignUpForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = (event) => {
    event.preventDefault();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 text-start">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#B57A3A]">Phone Number</label>
          <input
            type="tel"
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
            className={cn(
              "w-full bg-transparent border-0 border-b border-[#D5C7B4]",
              "py-2 outline-none text-sm text-[#5B4A3A]"
            )}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-[#B57A3A]">Username</label>
          <input
            type="text"
            className={cn(
              "w-full bg-transparent border-0 border-b border-[#D5C7B4]",
              "py-2 outline-none text-sm text-[#5B4A3A]"
            )}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-[#B57A3A]">Password</label>
          <div className="relative border-b border-[#D5C7B4]">
            <input
              type={showPassword ? "text" : "password"}
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
            Must contain a number and least of 6 characters
          </p>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-[#B57A3A]">Confirm Password</label>
          <div className="relative border-b border-[#D5C7B4]">
            <input
              type={showConfirmPassword ? "text" : "password"}
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
          <p className="text-xs text-[#B58B5A]">
            Must contain a number and least of 6 characters
          </p>
        </div>
      </div>

      <button
        type="submit"
        className={cn(
          "mt-2 w-full h-11 sm:h-12 rounded-md",
          "bg-[#262430] text-[#C49458]",
          "text-sm font-semibold tracking-wide",
          "shadow-md shadow-black/20"
        )}
      >
        Sign Up
      </button>
    </form>
  );
}

