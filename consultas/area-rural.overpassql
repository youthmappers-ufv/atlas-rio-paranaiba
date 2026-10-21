// Prancha 8 — Área rural: estradas vicinais, comunidades rurais e equipamentos rurais.
(
  way({{bbox}})[highway~"^(unclassified|track)$"];
  node({{bbox}})[place~"^(hamlet|isolated_dwelling|locality|farm)$"];
  nwr({{bbox}})[place=farm];
);
