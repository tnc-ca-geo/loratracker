define([
  'modules/filters',
  'modules/utils',
  'config/config',
], function (filters, utils, config) {

  function _repositionMap() {
    const transmissions = state.transmissions;
    const mostRecent = transmissions.reduce((acc, curr) => {
      const accDate = utils.parseDate(acc.attributes.time);
      const currDate = utils.parseDate(curr.attributes.time);
      return (accDate > currDate) ? acc : curr;
    }, transmissions.items[0]);
    const zoom = state.lastZoom ? state.lastZoom : 15;
    console.log('current zoom: ', state.mapView.zoom)
    console.log('zooming to: ', zoom);
    state.mapView.goTo({target: mostRecent, zoom: zoom}, {duration: 1000});
  };

  function _getStartDate(endDateString, duration) {
    duration = parseInt(duration);
    const ed = utils.parseDate(endDateString);
    const sd = new Date(ed - (duration * 60000));
    const y = sd.getFullYear(),
          m = ('0' + (sd.getMonth() + 1)).slice(-2),
          d  = ('0' + sd.getDate()).slice(-2),
          h = ('0' + sd.getHours()).slice(-2),
          min = ('0' + sd.getMinutes()).slice(-2),
          s = ('0' + sd.getSeconds()).slice(-2);
    return y + '-' + m + '-' + d + ' ' + h + ':' + min + ':' + s;
  }

  return {

    fetchData: async function() {
      
      // get most recent transmission
      let layer = state.loraLayer;
      let queryLastTransmission = layer.createQuery();
      queryLastTransmission.outStatistics = [config.outStatistics];
      const lastTrans = await layer.queryFeatures(queryLastTransmission);
      const end = lastTrans.features[0].attributes['time_last'];
      const start = _getStartDate(end, state.interval.items[0]);

      // query loraLayer service based on time filter
      let queryTransmissions = layer.createQuery();
      queryTransmissions.where = "time BETWEEN '" + start + 
        "' AND '" + end + "'";
      const response = await layer.queryFeatures(queryTransmissions);
      if (response.features.length === state.maxTransmissions) {
        alert(config.maxTransmissionsAlert);
      }

      // // for testing 
      // const maxRSSI = response.features.reduce((acc, curr) => {
      //   const accRSSI = acc.attributes.rssi;
      //   const currRSSI = curr.attributes.rssi;
      //   return (accRSSI > currRSSI) ? acc : curr;
      // }, response.features[0])

      // const minRSSI = response.features.reduce((acc, curr) => {
      //   const accRSSI = acc.attributes.rssi;
      //   const currRSSI = curr.attributes.rssi;
      //   return (accRSSI < currRSSI) ? acc : curr;
      // }, response.features[0])

      // console.log('rssi is between ' + minRSSI.attributes.rssi + ' and ' + maxRSSI.attributes.rssi)


      // update state
      state.transmissions.removeAll();
      state.transmissions.addMany(response.features);
    
    },

    handleNewData: async function() {
      _repositionMap();
      await filters.updateState();
      filters.updateDomElements();
    }

  }
})