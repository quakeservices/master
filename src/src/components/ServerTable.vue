<template>
  <div id="server-table">
    <v-data-table
      :loading="servers_loading"
      :headers="headers"
      :items="servers"
      :item-key="address"
      :items-per-page="20"
      :multi-sort="true"
      class="elevation-1"
    >
      <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>Servers</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
      </template>
      <template v-slot:item.players="{ item }">
        {{ item.players }} / {{ item.maxplayers }}
      </template>
      <template v-slot:item.password="{ item }">
        <template v-if="item.password == 1">Yes</template>
        <template v-else>No</template>
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
        headers:
        [
          {text: 'Hostname', value: 'hostname'},
          {text: 'Address', value: 'address'},
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
