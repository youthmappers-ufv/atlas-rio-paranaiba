// Prancha 1 — Localização e limites: sede, distritos, povoados e localidades.
// O limite municipal é baixado à parte (relação de atlas.toml).
(
  node({{bbox}})[place~"^(town|village|hamlet|locality|isolated_dwelling)$"];
);
