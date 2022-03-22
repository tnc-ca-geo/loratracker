define([
],
  function () {
    return {

      parseDate: (dateString) => {
        const dateTime = dateString.split(' ');
        const dateParts = dateTime[0].split('-');
        const timeParts = dateTime[1].split(':');
        const date = new Date(dateParts[0], dateParts[1] - 1, dateParts[2], 
          timeParts[0], timeParts[1], timeParts[2])
        return date;
      },

    }
})