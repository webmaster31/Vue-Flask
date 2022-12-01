<template>
  <v-app id="inspire">
    <navigation-drawer />
    <v-main>
      <app-loader class="loader" />
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import NavigationDrawer from "../components/Base/NavigationDrawer.vue";
import AppLoader from '../components/Base/AppLoader.vue';

export default {
  components: {
    NavigationDrawer,
    AppLoader
  }
}
</script>

<style lang="scss">
  .loader {
    position: absolute;
  }
</style>