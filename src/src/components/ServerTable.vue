<template>
  <div id="server-table">
    <v-data-table
      :loading="servers_loading"
      :headers="headers"
      :items="servers"
      :items-per-page="20"
      class="elevation-1"
    >
      <template v-slot:item.players="{ item }">
        {{ item.players }} / {{ item.maxplayers }}
      </template>
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
                   {text: 'Passworded', value: 'password'},
                   {text: 'Country', value: 'country'},
        ],
        servers: [],
        servers_loading: true
      }
    },
    mounted () {
      axios
        .get('https://api.quake.services')
        .then(response => (this.servers = response.data, 
                           this.servers_loading = false))
    }
  }
</script>

<style scoped>
</style>
