import nespressoLogo from "/assets/nespresso-logo.png";

export function SignUpHero() {
  return (
    <header className="flex flex-col gap-10">
      <div className="flex justify-center">
        <img src={nespressoLogo} alt="Nespresso" className="h-10 w-auto" />
      </div>

      <div className="flex flex-col gap-3 text-start">
        <div>
          <p className="text-4xl font-semibold text-[#B57A3A] leading-none">Hi!</p>
          <p className="text-5xl sm:text-6xl font-semibold text-[#B57A3A] leading-tight">
            Welcome
          </p>
        </div>
        <p className="text-sm sm:text-base text-[#B58B5A]">Let&apos;s create an account</p>
      </div>
    </header>
  );
}

