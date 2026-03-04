import { useNavigate } from "react-router-dom";
import { LoginLayout } from "./LoginLayout";
import { SignUpHero } from "./SignUpHero";
import { SignUpForm } from "./SignUpForm";

export function SignUpPage() {
  const navigate = useNavigate();

  const handleGoToLogin = () => {
    navigate("/login");
  };

  return (
    <LoginLayout>
      <SignUpHero />
      <SignUpForm />
      <div className="mt-10 text-center text-xs sm:text-sm text-[#B58B5A]">
        <span>Have an account ? </span>
        <button
          type="button"
          onClick={handleGoToLogin}
          className="font-semibold text-[#B57A3A]"
        >
          Log In
        </button>
      </div>
    </LoginLayout>
  );
}

