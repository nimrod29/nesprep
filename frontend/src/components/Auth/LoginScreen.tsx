import { useState, useCallback } from "react";
import type React from "react";
import { AuthLayout } from "./AuthLayout";
import { BrandPanel } from "./BrandPanel";
import { LoginCard } from "./LoginCard";

interface LoginScreenProps {
  onLogin: (name: string) => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [name, setName] = useState("");

  const handleSubmit = useCallback(
    (event: React.FormEvent) => {
      event.preventDefault();
      const trimmed = name.trim();
      if (trimmed) {
        onLogin(trimmed);
      }
    },
    [name, onLogin]
  );

  return (
    <AuthLayout
      brand={<BrandPanel />}
      content={
        <LoginCard
          name={name}
          onNameChange={setName}
          onSubmit={handleSubmit}
          isSubmitDisabled={!name.trim()}
        />
      }
    />
  );
}

