<template>
  <div id="server-table">
    <v-data-table
      :loading="servers_loading"
      :headers="headers"
      :items="servers"
      :items-per-page="20"
      class="elevation-1"
      show-expand
      single-expand
    >
      <template v-slot:item.players="{ item }">
        {{ item.players }} / {{ item.maxplayers }}
      </template>
      <template v-slot:item.password="{ item }">
        <template v-if="item.password == 1">Yes</template>
        <template v-else>No</template>
      </template>
      <template v-slot:expanded-item="{ item }">
        <td :colspan="headers.length">{{ item.address }}</td>
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
        headers: [ {text: 'Hostname', value: 'hostname'},
                   {text: 'Mode', value: 'gamename'},
                   {text: 'Map', value: 'mapname'},
                   {text: 'Players', value: 'players'},
                   {text: 'Password', value: 'password'},
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
