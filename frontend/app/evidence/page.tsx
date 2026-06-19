export default function EvidencePage() {
  return (
    <div className="p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold">
        GreenProof Evidence Record
      </h1>

      <div className="mt-6 border rounded-lg p-4">
        <p>
          <strong>Record ID:</strong> REC001
        </p>

        <p className="mt-2">
          <strong>Request:</strong> 500 grey tiles +
          tile cutter
        </p>

        <p className="mt-2">
          <strong>Selected Resources:</strong>
        </p>

        <ul className="list-disc ml-5">
          <li>Site A - 300 tiles</li>
          <li>Site B - 130 tiles</li>
          <li>Supplier F - 70 tiles</li>
          <li>Site D - Tile Cutter</li>
        </ul>

        <p className="mt-4">
          <strong>Excluded:</strong> Site E
        </p>

        <p className="mt-2">
          <strong>Savings:</strong> RM 3,400
        </p>

        <p className="mt-2">
          <strong>Carbon Avoided:</strong> 880 kg
          CO₂e
        </p>

        <p className="mt-2">
          <strong>Status:</strong> Approved
        </p>
      </div>
    </div>
  );
}