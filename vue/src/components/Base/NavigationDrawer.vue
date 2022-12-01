<template>
  <div>
    <v-navigation-drawer v-model="appDrawer" app :width="drawerWidth" class="elevation-0">
      <div class="pa-5 d-flex justify-center align-center brand-bg">
        <branding />
      </div>

      <div class="d-flex justify-center mt-8 align-center">
        <user-avatar />
      </div>

      <div class="text-center mt-4 font-weight-bold captialize-text" v-if="userInfo">{{ userInfo.full_name }}</div>

      <div class="text-center" v-if="userInfo">
        <small>{{ userInfo.email }}</small>
      </div>
    </v-navigation-drawer>
    <!-- 
      APP TOP BAR
    -->
    <v-app-bar app elevation="0">
      <v-app-bar-nav-icon @click="appDrawer = !appDrawer"></v-app-bar-nav-icon>
      <!-- <v-toolbar-title>Name</v-toolbar-title> -->
      <v-spacer />
      <div class="pr-2">
        <small>v</small>
        {{ appVersion }} 
      </div>

      <v-btn icon @click="goFull">
        <v-icon>mdi-fullscreen</v-icon>
      </v-btn>
      <main-dropdown />
    </v-app-bar>
  </div>
</template>

<script>
import versionInformation from '../../../version';
import { mainNavItems } from '../../static/nav';
import localService from '../../services/localService';

// COMPONENTS
import Branding from './Brand.vue';
import UserAvatar from "./UserAvatar.vue";
import MainDropdown from "./MainDropdown.vue";

export default {
  components: {
    Branding,
    UserAvatar,
    MainDropdown,
  },
  data: () => ({
    appDrawer: true,
    drawerWidth: '230px',
    isFullScreen: true,
  }),
  computed: {
    appVersion() {
      return versionInformation['version'];
    },
    mainNavItems() {
      return mainNavItems;
    },
    userInfo() {
      return localService.getItem('userInfo');
    }
  },
  methods: {
    goFull() {
      const elem = document.documentElement;
      if (this.isFullScreen) {
        if (elem.requestFullscreen) {
          elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
          elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
          elem.msRequestFullscreen();
        }
        this.isFullScreen = !this.isFullScreen;
      } else {
         if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
        this.isFullScreen = !this.isFullScreen;
      } 
    }
  }
}
</script>

<style scoped>
  .brand-bg {
    background-color: #F5F5F5;
  }
  .captialize-text {
    text-transform: capitalize;
  }
</style>