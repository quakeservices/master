<template>
  <div id="server-table">
    <v-data-table
      v-bind:headers="headers"
      :items="servers"
      class="elevation-1"
    >
    </v-data-table>
  </div>
</template>

<script>
  export default {
    name: 'server-table',
    props: {
      headers: Array,
      servers: Array,
    },
  }
</script>

<style scoped>
</style>
