export default function Button({
  children,
  onClick,
  variant = "primary",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary";
}) {
  return (
    <button
      onClick={onClick}
      className={
        variant === "primary"
          ? "w-full bg-black text-white py-3 rounded-xl font-medium hover:bg-gray-800 transition"
          : "w-full bg-white border py-3 rounded-xl font-medium hover:bg-gray-50 transition"
      }
    >
      {children}
    </button>
  );
}