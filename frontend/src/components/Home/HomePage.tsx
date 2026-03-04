import { useState, useCallback } from "react";
import { HomeLayout } from "./HomeLayout";
import { HomeHeader } from "./HomeHeader";
import { HomeTitle } from "./HomeTitle";
import { HomeChatPrompt } from "./HomeChatPrompt";

interface HomePageProps {
  onSubmitPrompt?: (text: string) => void;
}

export function HomePage({ onSubmitPrompt }: HomePageProps) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;
      if (onSubmitPrompt) {
        onSubmitPrompt(trimmed);
      }
    },
    [onSubmitPrompt]
  );

  return (
    <HomeLayout header={<HomeHeader />}>
      <div className="mt-[18vh] sm:mt-[20vh] flex flex-col items-center gap-10">
        <HomeTitle />
        <HomeChatPrompt value={prompt} onChange={setPrompt} onSubmit={handleSubmit} />
      </div>
    </HomeLayout>
  );
}



