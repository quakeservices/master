var apiURL = 'http://192.168.124.84:5000'

var shenanigans = new Vue({

  el: '#app',

  data: {
    headers: [
      { text: 'Hostname', value: 'hostname' },
      { text: 'Address', value: 'address' },
      { text: 'Map', value: 'map' },
      { text: 'Protected', value: 'protected' },
      { text: 'Players', value: 'players' },
      { text: 'Max Players', value: 'maxplayers' }
    ],
    items: null,
    showModal: false
  },

  created: function () {
    this.fetchData()
  },

  watch: {
    currentBranch: 'fetchData'
  },

  filters: {
    truncate: function (v) {
      var newline = v.indexOf('\n')
      return newline > 0 ? v.slice(0, newline) : v
    },
  },

  methods: {
    fetchData: function () {
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', apiURL)
      xhr.onload = function () {
        self.items = JSON.parse(xhr.responseText)
      }
      xhr.send()
    }
  }
})

