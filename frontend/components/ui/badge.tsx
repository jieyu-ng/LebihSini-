export default function Badge({
  label,
  type = "green",
}: {
  label: string;
  type?: "green" | "amber" | "red" | "gray";
}) {
  const map = {
    green: "bg-green-100 text-green-700",
    amber: "bg-yellow-100 text-yellow-700",
    red: "bg-red-100 text-red-700",
    gray: "bg-gray-200 text-gray-700",
  };

  return (
    <span className={`text-xs px-2 py-1 rounded-full ${map[type]}`}>
      {label}
    </span>
  );
}