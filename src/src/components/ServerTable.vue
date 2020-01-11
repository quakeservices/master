<template>
  <div id="server-table">
    <v-data-table
      :items="servers"
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
        servers: null
      }
    },
    mounted () {
      axios
        .get('https://hfgvort671.execute-api.us-west-2.amazonaws.com/prod')
        .then(response => (this.servers = response))
    }
  }
</script>

<style scoped>
</style>
