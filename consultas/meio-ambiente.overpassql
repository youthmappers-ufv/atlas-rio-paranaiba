// Prancha 6 — Meio ambiente: hidrografia, áreas verdes e vegetação.
(
  way({{bbox}})[waterway~"^(river|stream)$"];
  nwr({{bbox}})[natural~"^(water|wood|wetland|spring)$"];
  nwr({{bbox}})[landuse=forest];
  nwr({{bbox}})[leisure=nature_reserve];
  nwr({{bbox}})[boundary=protected_area];
);
