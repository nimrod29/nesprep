/**
 * ChatErrorBanner - displays connection/chat errors with retry option.
 */

import { AlertCircle, X, RefreshCw } from "lucide-react";
import { cn } from "@/shared/utils";

interface ChatErrorBannerProps {
  error: string | null;
  onDismiss: () => void;
  onRetry?: () => void;
}

export function ChatErrorBanner({
  error,
  onDismiss,
  onRetry,
}: ChatErrorBannerProps) {
  if (!error) return null;

  return (
    <div
      className={cn(
        "mb-2 p-3 rounded-lg",
        "bg-red-50/80",
        "border border-red-200/60",
        "flex items-center gap-3"
      )}
    >
      <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
      <p className="flex-1 text-sm text-red-700">
        {error}
      </p>
      <div className="flex items-center gap-1">
        {onRetry && (
          <button
            onClick={onRetry}
            className="p-1.5 rounded-md transition-colors text-red-500 hover:text-red-700 hover:bg-red-100"
            title="נסה שוב"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        )}
        <button
          onClick={onDismiss}
          className="p-1.5 rounded-md transition-colors text-red-500 hover:text-red-700 hover:bg-red-100"
          title="סגור"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
