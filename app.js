var apiURL = 'http://192.168.124.84:5000/'

var shenanigans = new Vue({

  el: '#app',

  data: {
    headers: [
      { text: 'Hostname',
        value: 'hostname',
        align: 'left' },
      { text: 'Address', value: 'address' },
      { text: 'Map', value: 'map' },
      { text: 'Password', value: 'needpass' },
      { text: 'Players', value: 'clients' },
    ],
    jsondata: null,
    items: [],
    currentGame: 'q2',
    gameType: 'All',
    gameTypes: null,
    drawer: false,
    hide_empty: false,
    hide_full: false,
    hide_protected: false,
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
        self.jsondata = JSON.parse(xhr.responseText)
      }
      xhr.send()
    },
    processData: function () {
      var self = this
      self.items = []
      self.gameTypes = []
      self.jsondata.forEach(function(server)
      {
        show = true
        if (self.hide_empty && server.clients == '0') { show = false; }
        if (self.hide_full && server.clients >= server.maxclients ) { show = false; }
        if (self.hide_protected && server.needpass != '0') { show = false; };
        if (server.gamename != self.gameType && self.gameType != 'All') { show = false };
        if (show) {
          self.items.push(server)
        }
      });
      self.gameTypes = [...new Set(self.jsondata.map(item => item.gamename))];
      self.gameTypes.unshift({text: 'All'})
    }
  },

  watch: {
    jsondata: 'processData',
    hide_empty: 'processData',
    hide_full: 'processData',
    hide_protected: 'processData',
    gameType: 'processData',
  },
})
