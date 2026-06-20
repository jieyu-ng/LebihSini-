const steps = [
  "Request",
  "Confirm",
  "Resources",
  "Verdict",
  "Evidence",
];

export default function ProgressStepper({
  currentStep,
}: {
  currentStep: number;
}) {
  return (
    <div className="flex justify-between mb-6 text-xs">
      {steps.map((step, index) => (
        <div
          key={step}
          className="flex flex-col items-center flex-1"
        >
          <div
            className={`
              w-8 h-8 rounded-full flex items-center justify-center
              ${
                index + 1 <= currentStep
                  ? "bg-green-600 text-white"
                  : "bg-slate-200 text-slate-600"
              }
            `}
          >
            {index + 1}
          </div>

          <span className="mt-1 text-center">
            {step}
          </span>
        </div>
      ))}
    </div>
  );
}