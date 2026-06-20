export interface Resource {
  id: string;
  name: string;
  type: string;

  quantity: number;

  distanceKm: number;

  risk: "green" | "amber" | "red";

  verificationStatus: string;

  selected: boolean;
}