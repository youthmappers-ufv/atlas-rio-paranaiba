// Prancha 2 — Sistema viário: vias por categoria e pavimento; pontes.
(
  way({{bbox}})[highway~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|track)(_link)?$"];
  way({{bbox}})[bridge][highway];
);
