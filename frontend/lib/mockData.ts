export const resources = [
  {
    id: "SITE_A",
    name: "Site A",
    type: "Reuse Material",

    quantity: 300,

    distanceKm: 14,

    risk: "green",

    verificationStatus: "Verified",

    selected: true,
  },

  {
    id: "SITE_B",
    name: "Site B",
    type: "Reuse Material",

    quantity: 130,

    distanceKm: 21,

    risk: "amber",

    verificationStatus: "Inspection Required",

    selected: true,
  },

  {
    id: "SITE_D",
    name: "Site D",

    type: "Equipment",

    quantity: 1,

    distanceKm: 9,

    risk: "green",

    verificationStatus: "Verified",

    selected: true,
  },

  {
    id: "SITE_E",

    name: "Site E",

    type: "Reuse Material",

    quantity: 200,

    distanceKm: 18,

    risk: "red",

    verificationStatus:
      "Product label unreadable",

    selected: false,
  },

  {
    id: "SUPPLIER_F",

    name: "Supplier F",

    type: "New Material",

    quantity: 70,

    distanceKm: 32,

    risk: "green",

    verificationStatus: "Commercial Supply",

    selected: true,
  },
];

export const plans = {
  normal: {
    title: "Buy Everything New",

    reusedTiles: 0,

    newTiles: 500,

    collectionSites: 1,

    cost: 12500,

    carbon: 1600,
  },

  partial: {
    title: "Partial Reuse",

    reusedTiles: 300,

    newTiles: 200,

    collectionSites: 2,

    cost: 10500,

    carbon: 1100,
  },

  greenproof: {
    title: "GreenProof Plan",

    reusedTiles: 430,

    newTiles: 70,

    collectionSites: 4,

    cost: 9100,

    carbon: 720,
  },
};