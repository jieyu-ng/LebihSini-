export default function PrimaryButton({
  text,
  onClick,
}: {
  text: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="
        w-full
        bg-green-600
        text-white
        py-3
        rounded-xl
        font-medium
        hover:bg-green-700
      "
    >
      {text}
    </button>
  );
}