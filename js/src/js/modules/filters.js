define([
  'esri/core/Collection'
], function (Collection) {

  function _addCheckbox(filterGroup, filter, toggledOn) {
    let checkbox = document.createElement('div');
    checkbox.classList.add('filter');
    let input = document.createElement('input');
    input.type = 'checkbox';
    input.name = filter;
    input.value = filter;
    input.checked = toggledOn;
    let label = document.createElement('label')
    label.for = filter;
    label.innerHTML = filter;
    checkbox.append(input, label);
    state.filterContainers[filterGroup].append(checkbox);
  };

  function _getNewFilterState(newFilters, oldFilterState) {
    let newFilterState = new Collection();
    newFilters.forEach((newFilter) => {
      let match = oldFilterState.find(oldFilter => (
        oldFilter.name === newFilter.name
      ));
      if (match) {
        oldFilterState.remove(match);
        match.visible = true;
        newFilterState.add(match);
      } else {
        newFilter.toggledOn = true;
        newFilter.visible = true;
        newFilterState.add(newFilter)
      }
    });
    oldFilterState.forEach(oldFilter => {
      oldFilter.visible = false;
      newFilterState.add(oldFilter);
    });
    return newFilterState;
  }

  function _removeDupes(values) {
    let uniqueValues = [];
    values.forEach((item, i) => {
      if (
        (uniqueValues.length < 1 || uniqueValues.indexOf(item) === -1) &&
        item !== ''
      ) {
        uniqueValues.push(item);
      }
    });
    return uniqueValues;
  }

  function _getFilters(transmissions) {
    let filters = [];
    const attributes = ['dev', 'gateway'];
    attributes.forEach(attr => {
      const allValues = transmissions.map(trans => trans.attributes[attr] );
      const uniqueValues = _removeDupes(allValues);
      const filts = uniqueValues.map(value => (
        { name: value, filterGroup: attr }
      ));
      filters = filters.concat(filts);
    });
    return filters;
  };

  function _handleFilterChange(event) {
    if (event.target.name === 'interval') {
      state.lastZoom = state.mapView.zoom;
      state.interval.removeAll();
      state.interval.add(event.target.value)
    } else {
      let newFilters = state.filters.clone();
      newFilters.forEach(filt => {
        if (filt.name === event.target.value) {
          filt.toggledOn = event.target.checked;
        }
      });
      state.filters.removeAll();
      state.filters.addMany(newFilters);
    }
  };

  return {

    init: () => {
      state.filterContainers = {
        interval: document.getElementById('intervalFilter'),
        dev: document.getElementById('devFilter'),
        gateway: document.getElementById('gatewayFilter'),
      };
      for (const container of Object.values(state.filterContainers)) {
        container.onchange = function(event) { _handleFilterChange(event) };
      }
    },

    updateState: () => {
      const newFilters = _getFilters(state.transmissions);
      const oldFilterState = state.filters.clone();
      let newFilterState = _getNewFilterState(newFilters, oldFilterState);
      state.filters.removeAll();
      state.filters.addMany(newFilterState);
    },

    updateDomElements: () => {
      ['dev', 'gateway'].forEach((filterGroup) => {
        const container = state.filterContainers[filterGroup];
        while (container.firstChild) {
          container.removeChild(container.firstChild);
        }
        const filters = state.filters.filter(filter => (
          filter.filterGroup === filterGroup
        ));
        filters.forEach((filter) => {
          if (filter.visible) {
            _addCheckbox(filterGroup, filter.name, filter.toggledOn);
          }
        });
      });
    },
  }
})