<template>
  <div id="server-table">
    <v-data-table
      :headers="headers"
      :items="servers"
      :items-per-page="20"
      class="elevation-1"
    >
    </v-data-table>
  </div>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'server-table',
    data () {
      return {
        headers: [ {text: 'Address', value: 'address'},
                   {text: 'Hostname', value: 'hostname'},
                   {text: 'Map', value: 'mapname'},
                   {text: 'Players', value: 'players'},
                   {text: 'Max Players', value: 'maxplayers'},
                   {text: 'Passworded', value: 'password'},
                   {text: 'Country', value: 'country'},
        ],
        servers: [],
      }
    },
    mounted () {
      axios
        .get('https://api.quake.services')
        .then(response.data => (this.servers = response.data))
    }
  }
</script>

<style scoped>
</style>
