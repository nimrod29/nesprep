import nespressoLogo from "/assets/nespresso-logo.png";

export function ForgotPasswordHero() {
  return (
    <header className="flex flex-col gap-10">
      <div className="flex justify-center">
        <img src={nespressoLogo} alt="Nespresso" className="h-10 w-auto" />
      </div>

      <div className="flex flex-col gap-4 text-start">
        <div>
          <p className="text-4xl font-semibold text-[#B57A3A] leading-none">Oh, no!</p>
          <p className="text-5xl sm:text-6xl font-semibold text-[#B57A3A] leading-tight">
            I forgot
          </p>
        </div>
        <p className="text-sm sm:text-base text-[#B58B5A] max-w-md">
          Enter your phone number or username, and we’ll send you a link to reset your password.
        </p>
      </div>
    </header>
  );
}

