export default function Card({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white border rounded-xl shadow-sm p-5">
      {children}
    </div>
  );
}