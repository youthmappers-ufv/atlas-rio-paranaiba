// Prancha 9 (proposta) — Cultura, turismo e lazer.
(
  nwr({{bbox}})[tourism];
  nwr({{bbox}})[historic];
  nwr({{bbox}})[amenity~"^(place_of_worship|theatre|arts_centre|library|community_centre|events_venue|cinema|restaurant|cafe|bar|pub|fast_food|ice_cream)$"];
  nwr({{bbox}})[leisure~"^(park|stadium|sports_centre|sports_hall|playground|fitness_station|nature_reserve)$"];
  nwr({{bbox}})[natural~"^(waterfall|peak|cave_entrance)$"];
  nwr({{bbox}})[waterway=waterfall];
);
