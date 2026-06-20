export default function Card({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="
      bg-white
      rounded-xl
      p-4
      shadow-sm
      border
      "
    >
      {children}
    </div>
  );
}