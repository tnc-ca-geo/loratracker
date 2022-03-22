import React, { useRef, useEffect } from 'react';
import esriConfig from '@arcgis/core/config';
import ArcGISMap from '@arcgis/core/Map';
import MapView from '@arcgis/core/views/MapView';
import styles from './Map.module.css';
import '@arcgis/core/assets/esri/css/main.css';
import '@arcgis/core/assets/esri/themes/dark/main.css';


/* const StyledMap = styled.div`
  padding: 0;
  margin: 0;
  width: 20%;
  height: 20%;
`*/

esriConfig.apiKey = "AAPKf03263028e5a474b8f8827a99f6057d40Rqsrhh04CBME4268jUQh1PrrDBprYFlAppXnq3NxCmOoGJhlZpgSsnuHJjnpUhh"


export const MapContainer = () => {
  const mapRef = useRef();
  useEffect(
    /* what you want to do */
    () => {
      const map = new ArcGISMap({
        basemap: 'osm-standard'
      });
      const view = new MapView({
        container: mapRef.current,
        map: map,
        center: [-118, 34],
        zoom: 8
      });
    },
    /* when you want to do it*/
    []
  )
  return <div ref={mapRef} className={styles.mapDiv} />
};
