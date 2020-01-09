<template>
  <v-app dark>
    <v-app-bar
      app
    >
      Quake Servers
      <v-spacer></v-spacer>

    </v-app-bar>

    <v-content>
      <Servers/>
    </v-content>
  </v-app>
</template>

<script>
import Servers from './components/Servers';

export default {
  name: 'App',

  components: {
    Servers,
  },
};
</script>
