import { cn } from "@/utils";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  text?: string;
}

const sizeMap = {
  sm: "w-5 h-5 border-2",
  md: "w-8 h-8 border-3",
  lg: "w-12 h-12 border-4",
};

export default function LoadingSpinner({
  size = "md",
  className,
  text,
}: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      <div
        className={cn(
          "border-sky-500 border-t-transparent rounded-full animate-spin",
          sizeMap[size]
        )}
        style={{ borderWidth: size === "lg" ? 4 : size === "md" ? 3 : 2 }}
      />
      {text && <p className="text-slate-400 text-sm">{text}</p>}
    </div>
  );
}
