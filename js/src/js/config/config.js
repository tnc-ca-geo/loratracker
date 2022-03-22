define([],
  function () {
    return {

      map: {
        basemap: 'topo-vector',
      },

      mapView: {
        container: 'map',
        map: map,
        center: [-120, 37.25],
        zoom: 6
      },
    
      loraLayer: {
        title: 'Lora tracking',
        url: 'https://services.arcgis.com/F7DSX1DSNSiWmOqh/' +
          'arcgis/rest/services/lora_tracking/FeatureServer',
        outFields: ['*'],
      },

      // for querying endpoint for most recent transmission
      outStatistics: {
        onStatisticField: 'time',
        outStatisticFieldName: 'time_last',
        statisticType: 'max'
      },

      transmissionLayer: {
        objectIdField: 'FID',
        geometryType: 'point',
        fields: [
          {
            name: 'FID',
            type: 'oid',
          },
          {
            name: 'time',
            type: 'string',
          },
          {
            name: 'received_t',
            type: 'string',
          },
          {
            name: 'app',
            type: 'string',
          },
          {
            name: 'dev',
            type: 'string',
          },
          {
            name: 'frames',
            type: 'integer',
          },
          {
            name: 'gateway',
            type: 'string',
          },
          {
            name: 'rssi',
            type: 'integer',
          },
          {
            name: 'dr',
            type: 'string',
          },
          {
            name: 'cr',
            type: 'string',
          },
          {
            name: 'snr',
            type: 'string',
          },
          {
            name: 'f_mhz',
            type: 'single',
          },
          {
            name: 'airtime_ms',
            type: 'integer',
          },
          {
            name: 'gtw_count',
            type: 'integer',
          },
        ],
  
        renderer: {
          type: 'simple',  // autocasts as new SimpleRenderer()
          symbol: {
            type: 'simple-marker',  // autocasts as new SimpleMarkerSymbol()
            size: 6,
            color: 'black',
          },
          visualVariables: [{
            type: 'color',
            field: 'rssi',
            stops: [
              // { value: -100, color: '#f9ddda' },
              // { value: -50, color: '#ce78b3' },
              // { value: 0, color: '#573b88' }

              // { value: -120, color: '#213c47' },
              // { value: 0, color: '#89efc6' },

              // { value: -150, color: '#003f5c' },
              // { value: -75, color: '#bc5090' },
              // { value: 0, color: '#ffa600' }

              // { value: -150, color: '#D2222D' },  // red
              // { value: -75, color: '#FFBF00' },   // yellow
              // { value: 0, color: '#6bd084' },      // green

              { value: -120, color: '#cf597e' },
              { value: -100, color: '#e88471' },
              { value: -80, color: '#eeb479' },
              { value: -60, color: '#e9e29c' },
              { value: -40, color: '#9ccb86' },
              { value: -20, color: '#39b185' },
              { value: 0, color: '#009392' },




            ],
            legendOptions: {
              title: 'RSSI'
            }
          }],
        },
  
        popupTemplate: {
          title: 'Device: {dev}',
          content: 
            '<ul>' +
              '<li><span>RSSI:</span> {rssi}</li>' + 
              '<li><span>Gateway:</span> {gateway}</li>' + 
              '<li><span>Gateway count:</span> {gtw_count}</li>' + 
              '<li><span>Time:</span> {time}</li>' + 
              '<li><span>Recieved Time:</span> {received_t}</li>' + 
              '<li><span>dr:</span> {dr}</li>' + 
              '<li><span>cr:</span> {cr}</li>' + 
              '<li><span>snr:</span> {snr}</li>' + 
              '<li><span>Airtime:</span> {airtime_ms}</li>' + 
              '<li><span>Frames:</span> {frames}</li>' + 
            '</ul>'
          ,
        }
        
      },

      maxTransmissionsAlert: 'You have exceeded the maximum number of ' +
        'transmissions the server can return.',

    }
})