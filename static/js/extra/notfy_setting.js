const notyf = new Notyf({
  duration: 4000,
  ripple: true,
  dismissible: true,
  position: {
    x: 'center',
    y: 'top'
  },
  types: [
    {
      type: 'success',
      background: '#28a745',
      icon: {
        className: 'material-icons',
        text: 'check_circle',
      }
    },
    {
      type: 'error',
      background: '#dc3545',
      icon: {
        className: 'material-icons',
        text: 'error',
      }
    }
  ]
});