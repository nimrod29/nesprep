import { cn } from "@/shared/utils";

export function ForgotPasswordForm() {
  const handleSubmit: React.FormEventHandler<HTMLFormElement> = (event) => {
    event.preventDefault();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6 text-start">
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-[#B57A3A]">Username, or Phone Number</label>
        <input
          type="text"
          className={cn(
            "w-full bg-transparent border-0 border-b border-[#D5C7B4]",
            "py-2 outline-none text-sm text-[#5B4A3A]"
          )}
        />
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
        Forgot Password
      </button>

      <div className="mt-10 text-center text-xs sm:text-sm text-[#B58B5A]">
        <span>Don&apos;t have an account ? </span>
        <button type="button" className="font-semibold text-[#B57A3A]">
          Sign Up
        </button>
      </div>
    </form>
  );
}

