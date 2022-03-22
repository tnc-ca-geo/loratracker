define([
  'dojo/query',
  'dojo/dom-class',
  'esri/widgets/Locate',
  'esri/Graphic',
  'esri/widgets/Expand',
  'modules/data',
],
  function (dojoQuery, domClass, Locate, Graphic, Expand, data) {

    function _initZoomBlocker() {
      // Block pinch zooming on popup
      let popupContainer = document.getElementsByClassName('esri-popup')[0];
      popupContainer.addEventListener('touchmove', event => {
        if (event.scale !== 1) { event.preventDefault(); }
      }, false);

      // Block double-tap zooming on popup
      let lastTouchEnd = 0;
      popupContainer.addEventListener('touchend', event => {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) { event.preventDefault(); }
        lastTouchEnd = now;
      }, false);
    };

    return {

      init: () => {
        const view = state.mapView;

        view.ui.move('zoom', 'bottom-right');
        view.popup.collapseEnabled = false;

        let locateWidget = new Locate({
          view: view,
          graphic: new Graphic({
            symbol: { type: 'simple-marker' }
          })
        });
        view.ui.add(locateWidget, 'bottom-left');
    
        const filterContainer = dojoQuery('#filters')[0];    
        let expand = new Expand({
          expandIconClass: 'esri-icon-filter',
          view: view,
          content: filterContainer,
        });
        view.ui.add(expand, 'top-right', 0);

        view.ui.add('refresh-button', 'top-right', 1);
        dojoQuery('#refresh-button').on('click', function() {
          domClass.add(this, 'animate');
          setTimeout(() => domClass.remove(this, 'animate'), 1000);
          state.lastZoom = state.mapView.zoom;
          data.fetchData();
        });

        _initZoomBlocker();

      }

    }
})