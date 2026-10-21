// Prancha 7 — Mobilidade e acessibilidade: pontos de ônibus, calçadas, travessias, rampas.
(
  node({{bbox}})[highway=bus_stop];
  node({{bbox}})[public_transport=platform];
  way({{bbox}})[footway=sidewalk];
  nwr({{bbox}})[highway=crossing];
  node({{bbox}})[kerb];
);
