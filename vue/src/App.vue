<template>
  <v-app id="app">
    <notifications />
    <router-view />
  </v-app>
</template>

<script>
import localService from './services/localService';

export default {
  methods: {
    checkIfUserIsLoggedIn() {
      const userInfo = localService.getItem('userInfo');
      const token = localService.getItem('token');

      if (userInfo && token) {
        const loginType = localService.getItem('loginType');
        if (loginType) {
          this.$store.commit('login/setState', { key: 'loginType', value: loginType });
        }
        this.$store.commit('login/setState', { key: 'currentUser', value: userInfo });
        return this.$store.commit('login/setState', { key: 'isLoggedIn', value: true });
      }
      return this.$store.commit('login/setState', { key: 'isLoggedIn', value: false });
    }
  },
  mounted() { 
    this.checkIfUserIsLoggedIn();
  }
}
</script>


<style>
  /* SHARED STYLES */
  #app {
    font-family: 'Montserrat', sans-serif;
  }
  
  .absolute-loader {
    position: absolute;
  }
</style>