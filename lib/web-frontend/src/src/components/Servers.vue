<template>
  <div id="server">
    <server-table />
  </div>
</template>

<script>
  import ServerTable from '@/components/ServerTable.vue'

  export default {
    name: 'servers',
    components: {
      ServerTable,
    },
  }
</script>

<style scoped>
</style>
