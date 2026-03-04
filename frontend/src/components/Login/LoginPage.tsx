import { LoginLayout } from "./LoginLayout";
import { LoginHero } from "./LoginHero";
import { LoginForm } from "./LoginForm";

export function LoginPage() {
  return (
    <LoginLayout>
      <LoginHero />
      <LoginForm />
    </LoginLayout>
  );
}

