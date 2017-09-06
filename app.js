var apiURL = 'http://192.168.124.84:5000/'

var shenanigans = new Vue({

  el: '#app',

  data: {
    headers: [
      { text: 'Hostname', value: 'hostname' },
      { text: 'Address', value: 'address' },
      { text: 'Map', value: 'map' },
      { text: 'Password', value: 'needpass' },
      { text: 'Players', value: 'clients' },
    ],
    data: null,
    items: [],
    currentGame: 'q2',
    drawer: false,
    hide_empty: false,
    hide_full: false,
    hide_protected: false
  },

  created: function () {
    this.fetchData()
  },

  beforeMount: function () {
    this.processData()
  },

  methods: {
    fetchData: function () {
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', apiURL + self.currentGame + '/servers')
      xhr.onload = function () {
        self.data = JSON.parse(xhr.responseText)
      }
      xhr.send()
    },
    processData: function () {
      var self = this
      console.log(self.data)
      self.items = []
      self.data.forEach(function(server)
      {
        show = true
        if (self.hide_empty && server.clients == '0') { show = false; }
        if (self.hide_full && server.clients >= server.maxclients ) { show = false; }
        if (self.hide_protected && server.needpass != '0') { show = false; };
        if (show) {
          self.items.push(server)
        }
      });
    }
  },

  watch: {
    data: 'processData',
    hide_empty: 'processData',
    hide_full: 'processData',
    hide_protected: 'processData',
  },
})
