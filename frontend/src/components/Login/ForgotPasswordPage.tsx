import { LoginLayout } from "./LoginLayout";
import { ForgotPasswordHero } from "./ForgotPasswordHero";
import { ForgotPasswordForm } from "./ForgotPasswordForm";

export function ForgotPasswordPage() {
  return (
    <LoginLayout>
      <ForgotPasswordHero />
      <ForgotPasswordForm />
    </LoginLayout>
  );
}

