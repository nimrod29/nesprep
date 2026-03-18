import { useState, useCallback } from "react";
import { HomeLayout } from "./HomeLayout";
import { HomeHeader } from "./HomeHeader";
import { HomeTitle } from "./HomeTitle";
import { HomeChatPrompt } from "./HomeChatPrompt";
import { LoginModal } from "./LoginModal";

const PENDING_PROMPT_KEY = "nesprep-pending-prompt";

export function HomePage() {
  const [prompt, setPrompt] = useState("");
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleSubmit = useCallback((text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    sessionStorage.setItem(PENDING_PROMPT_KEY, trimmed);
    setShowLoginModal(true);
  }, []);

  const handleLoginSuccess = useCallback(() => {
    setShowLoginModal(false);
  }, []);

  return (
    <HomeLayout header={<HomeHeader onLoginClick={() => setShowLoginModal(true)} />}>
      <div className="mt-[18vh] sm:mt-[20vh] flex flex-col items-center gap-10">
        <HomeTitle />
        <HomeChatPrompt value={prompt} onChange={setPrompt} onSubmit={handleSubmit} />
      </div>
      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
          onSuccess={handleLoginSuccess}
        />
      )}
    </HomeLayout>
  );
}



