<template>
  <v-avatar color="#172950" :size="size">
    <img v-if="userProfileImage" :src="userProfileImage" />
    <span v-else class="white--text text-h4">{{ initials }}</span>
  </v-avatar>
</template>

<script>
import localService from '../../services/localService';

export default {
  props: {
    size: {
      type: String,
      default: () => '90'
    }
  },
  computed: {
    userInfo() {
      return localService.getItem('userInfo');
    },
    initials() {
      if (this.userInfo) {
        const splitName = this.userInfo.full_name.split(' ');
        return splitName[0].charAt(0).toUpperCase() + splitName[1].charAt(0).toUpperCase();
      }
    },
    userProfileImage() {
      if (this.userInfo.profileImage && this.userInfo.profileImage.length > 0)
        return this.userInfo.profileImage;
      return null;
    }
  }
}
</script>

<style>

</style>