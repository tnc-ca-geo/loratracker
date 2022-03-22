define([
  'config/config',
],
  function (config) {

    function _getApprovedFilters(filterGroup) {
      let approvedFilters = state.filters
        .filter(filter => (
          (filter.filterGroup === filterGroup)
             && filter.toggledOn
             && filter.visible
        ))
        .map(filter => filter.name );
      return approvedFilters;
    }
  
    async function _updateGraphics(transmissions) {
      let featuresToDelete = await state.transmissionsLayerView.queryFeatures();
      const featuresToAdd = transmissions.map(graphic => {
        graphic.symbol = config.transmissionLayer.renderer.symbol;
        return graphic;
      });
      state.transmissionsLayer.applyEdits({
        deleteFeatures: featuresToDelete.features,
        addFeatures: featuresToAdd,
      });
    }
  
    return {

      applyFilters: function() {
        const approvedDevices = _getApprovedFilters('dev');
        const approvedGateways = _getApprovedFilters('gateway');
        const transmissions = state.transmissions;
        const filteredTransmissions = transmissions.filter(trans => (
          approvedDevices.includes(trans.attributes.dev) && 
          approvedGateways.includes(trans.attributes.gateway)
        ));
        _updateGraphics(filteredTransmissions);
      }

    }
})