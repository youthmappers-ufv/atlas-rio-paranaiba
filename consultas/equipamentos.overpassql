// Prancha 5 — Equipamentos e serviços públicos.
(
  nwr({{bbox}})[amenity~"^(townhall|social_facility|police|fire_station|post_office|courthouse|community_centre|library|marketplace|grave_yard)$"];
  nwr({{bbox}})[office=government];
  nwr({{bbox}})[landuse=cemetery];
  nwr({{bbox}})[leisure~"^(park|pitch|sports_centre|stadium|playground)$"];
);
