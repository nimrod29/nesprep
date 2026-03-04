import { cn } from "@/shared/utils";
import { useNavigate } from "react-router-dom";

export function HomeHeader() {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate("/login");
  };

  return (
    <div className="flex items-center justify-between">
      <button
        type="button"
        onClick={handleLoginClick}
        className={cn(
          "inline-flex items-center justify-center rounded-full",
          "h-10 px-[22px] text-[15px] font-medium",
          "bg-[#1A1A1A] text-white hover:bg-black/90",
          "shadow-[0_4px_12px_rgba(0,0,0,0.15)] transition-colors"
        )}
      >
        התחברות
      </button>
      <img src="/assets/nespresso-logo.png" alt="Nespresso" className="h-[22px] sm:h-[24px] w-auto" />
    </div>
  );
}

