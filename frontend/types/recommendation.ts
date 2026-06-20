export interface Recommendation {
  verdict: string;

  costSaving: number;

  carbonSaving: number;

  reusedTiles: number;

  newTiles: number;

  confidence: number;
}