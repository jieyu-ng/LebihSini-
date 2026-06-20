export const plans = {
  normal: {
    title: "Buy Everything New",

    reusedTiles: 0,
    newTiles: 500,
    collectionSites: 1,
    cost: 12500,
    carbon: 1600,

    // ADD THESE
    risk: "high",
    deadlineRisk: "low",
    equipmentSource: "External rental",
  },

  partial: {
    title: "Partial Reuse",

    reusedTiles: 300,
    newTiles: 200,
    collectionSites: 2,
    cost: 10500,
    carbon: 1100,

    risk: "medium",
    deadlineRisk: "medium",
    equipmentSource: "Mixed reuse + rental",
  },

  greenproof: {
    title: "GreenProof Plan",

    reusedTiles: 430,
    newTiles: 70,
    collectionSites: 4,
    cost: 9100,
    carbon: 720,

    risk: "low",
    deadlineRisk: "low",
    equipmentSource: "Fully optimised reuse network",
  },
};