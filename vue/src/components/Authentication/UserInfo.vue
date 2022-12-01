<template>
  <v-card outlined>
    <v-card-text>
      <div class="d-flex justify-center">
        <user-avatar :size="'70'" />
      </div>

      <v-row class="mt-4">
        <v-col cols="12" md="4" class="d-flex justify-end pr-6 font-weight-bold">Name</v-col>
        <v-col cols="12" md="8" class="capitalize">{{ userInfo.full_name }}</v-col>

        <v-col cols="12" md="4" class="d-flex justify-end pr-6 font-weight-bold">Email</v-col>
        <v-col cols="12" md="8">{{ userInfo.email }}</v-col>

        <v-col cols="12" md="4" class="d-flex justify-end pr-6 font-weight-bold">Verified</v-col>
        <v-col cols="12" md="8">
          <v-icon :color="userInfo.verified ? 'green' : 'red'">
            {{ userInfo.verified ? 'mdi-check-decagram' : 'mdi-close-circle' }}
          </v-icon>
        </v-col>

        <v-col cols="12" md="4" class="d-flex justify-end pr-6 font-weight-bold">MFA</v-col>
        <v-col cols="12" md="8">
          <v-icon :color="userInfo.mfa_enabled ? 'green' : 'red'">
            {{ userInfo.mfa_enabled ? 'mdi-check-decagram' : 'mdi-close-circle' }}
          </v-icon>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import UserAvatar from '../Main/UserAvatar.vue';
export default {
  components: {
    UserAvatar
  },
  computed: {
    userInfo() {
      return this.$store.getters['login/currentUser'];
    }
  }
}
</script>