import React from "react";
import { Map, Marker, Popup, TileLayer } from "react-leaflet";
import DungeonLayer from "./DungeonLayer";
import L from "leaflet";

// import "leaflet/dist/leaflet.css";

// delete L.Icon.Default.prototype._getIconUrl;

// L.Icon.Default.mergeOptions({
//   iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
//   iconUrl: require("leaflet/dist/images/marker-icon.png"),
//   shadowUrl: require("leaflet/dist/images/marker-shadow.png")
// });

const iconPerson = new L.Icon({
  iconUrl: require("./knight.png"),
  iconRetinaUrl: require("./knight.png"),
  iconSize: [24, 24],
  iconAnchor: [14, 24],
  popupAnchor: null,
  shadowUrl: null,
  shadowSize: null,
  popupAnchor: [0, -36],
  shadowAnchor: null,
  className: "custom-icon"
});

const position = [-0.097, 0.099];

export default () => {
  const [markers, setMarkers] = React.useState([]);

  const addMarker = e => {
    setMarkers([e.latlng]);
  };

  return (
    <Map
      center={position}
      zoom={13}
      touchZoom={false}
      scrollWheelZoom={false}
      doubleClickZoom={false}
      zoomControl={false}
      attributionControl={false}
      onClick={addMarker}
    >
      <DungeonLayer
        // url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution={null}
      />
      <Marker position={position} icon={iconPerson}>
        <Popup>You are here!</Popup>
      </Marker>
      {markers.map((position, idx) => (
        <Marker key={`marker-${idx}`} position={position}>
          <Popup>
            <span>Traveling here...</span>
          </Popup>
        </Marker>
      ))}
    </Map>
  );
};
