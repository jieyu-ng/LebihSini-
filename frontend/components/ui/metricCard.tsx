export default function MetricCard({
  label,
  value,
  subtext,
  tone = "neutral",
}: {
  label: string;
  value: string | number;
  subtext?: string;
  tone?: "green" | "red" | "neutral";
}) {
  const toneMap = {
    green: "text-green-600",
    red: "text-red-600",
    neutral: "text-gray-900",
  };

  return (
    <div className="border rounded-xl p-4 bg-white">
      <div className="text-xs text-gray-500">{label}</div>
      <div className={`text-lg font-semibold ${toneMap[tone]}`}>
        {value}
      </div>
      {subtext && (
        <div className="text-xs text-gray-500 mt-1">{subtext}</div>
      )}
    </div>
  );
}