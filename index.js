const fs = require('fs');
const data = JSON.parse(fs.readFileSync('./Vermont.geojson', 'utf8'));

const features = data.features

const comparison = {lat: 44.51630409200004, lng: -73.24221313699996}

const LAT_DIFF = 0.0004
const LNG_DIFF = 0.0006
let idx = 0
const found = []

// console.log(features[72769].geometry.coordinates[0].map(c => {return {lat: c[1], lng: c[0] }}))
for (const f of features) {
  const coords = f.geometry.coordinates[0]

  for (const c of coords) {
    const lat = c[1]
    const lng = c[0]
    const lat_diff = Math.abs(lat - comparison.lat)
    const lng_diff = Math.abs(lng - comparison.lng)
    if (lng_diff < LNG_DIFF && lat_diff < LAT_DIFF) {
      // console.log({ comp_lat: comparison.lat, comp_lng: comparison.lng, lat, lng, lng_diff, lat_diff})
      // console.log(JSON.stringify({ feature: f, index: idx}))
      found.push({ coords: coords.map(c => { return { lat: c[1], lng: c[0]}}), index: idx})
      break;
    }
  }
  idx++
}

// console.log(JSON.stringify(found, null, 2))

console.log(JSON.stringify(features[162116], null, 2))