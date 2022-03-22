require([
  'esri/core/Accessor',
  'esri/core/Collection',
  'esri/Map',
  'esri/views/MapView',
  'esri/layers/FeatureLayer',
  "esri/identity/IdentityManager",
  "esri/portal/Portal",
  "esri/portal/PortalQueryParams",
  "esri/identity/OAuthInfo",
  'modules/ui',
  'modules/data',
  'modules/filters',
  'modules/graphics',
  'config/config',
], function(Accessor, Collection, Map, MapView, FeatureLayer, esriId, Portal,
  PortalQueryParams, OAuthInfo, ui, data, filters, graphics, config) {

    const info = new OAuthInfo({
      // Swap this ID out with registered application ID
      appId: 'zOVXaFKB7YVG2XcT',
      // Uncomment the next line and update if using your own portal
      portalUrl: 'https://tnc.maps.arcgis.com/',
      // Uncomment the next line to prevent the user's signed in state from being shared with other apps on the same domain with the same authNamespace value.
      // authNamespace: "portal_oauth_inline",
      popup: false
    });

    esriId.registerOAuthInfos([info]);

    esriId
      .checkSignInStatus(info.portalUrl + "/sharing")
      .then(() => { init(); })
      .catch(() => { console.log("NOT SIGNED IN"); });

    esriId.getCredential(info.portalUrl); // + "/sharing");

  async function init() {

    // init state
    var State = Accessor.createSubclass({
      declaredClass: 'AppState',
      constructor: function() {
        this.interval = new Collection();
        this.filters = new Collection();
        this.filterContainers = null;
        this.transmissions = new Collection();
        this.maxTransmissions = null;
        this.mapView = null;
        this.loraLayer = null;
        this.transmissionsLayer = null;
        this.transmissionsLayerView = null;
        this.lastZoom = null;

      },
      properties: {
        interval: {},
        filters: {},
        filterContainers: {},
        transmissions: {},
        maxTransmissions: {},
        mapView: {},
        loraLayer: {},
        transmissionsLayer: {},
        transmissionsLayerView: {},
        lastZoom: {},
      },
    });
    state = new State();

    // init map
    let map = new Map(config.map);
    state.loraLayer = new FeatureLayer(config.loraLayer);
    await state.loraLayer.load();
    state.maxTransmissions = state.loraLayer.capabilities.query.maxRecordCount;
    state.transmissionsLayer = new FeatureLayer(config.transmissionLayer);
    state.transmissionsLayer.source = new Collection();
    map.add(state.transmissionsLayer);
    state.mapView = new MapView(config.mapView);
    state.mapView.map = map;

    state.mapView.ui.add("logoutDialog", "top-right");

    document.getElementById("logoutDialog").addEventListener("click", () => {
      esriId.destroyCredentials();
      window.location.reload();
    });

    await state.mapView.whenLayerView(state.transmissionsLayer)
      .then(lv => state.transmissionsLayerView = lv);

    state.mapView.when(function() {
      ui.init();
      filters.init();

      state.interval.on('change', data.fetchData);
      state.transmissions.on('change', data.handleNewData);
      state.filters.on('change', graphics.applyFilters);

      const intervalRadios = document.getElementsByName('interval');
      intervalRadios.forEach(radio => {
        if (radio.checked) { state.interval.add(radio.value) }
      });



    });

  };

  init();

});
