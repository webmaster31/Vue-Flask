<template>
  <v-card outlined>
    <v-card-title>
      <div class="d-flex align-center text-h6">
        Connected Social Accounts
      </div>
    </v-card-title>

    <v-card-text>
      <div v-for="(account) in getUserSocialAccounts" :key="account.profile.entity_id">
        <v-btn 
          v-if="['google', 'linkedin', 'github', 'facebook'].includes(account.provider)" 
          block outlined 
          :color="getButtonConfiguration(account.provider)[1]" 
          class="mb-2"
          @click="removeConnectedAccount(account, getButtonConfiguration(account.provider)[2], getButtonConfiguration(account.provider)[1])"
        >
          <v-icon>{{ getButtonConfiguration(account.provider)[2] }}</v-icon>
          <div>{{ getButtonConfiguration(account.provider)[0] }}</div>
        </v-btn>
      </div>
    </v-card-text>

    <!-- DIALOGS -->

    <v-dialog v-model="connectedAccountModal" width="400px" persistent>
      <v-card v-if="selectedToDelete">
        <v-card-title class="d-flex justify-space-between align-center">
          <div>Confirmation</div>
          <v-icon large :color="selectedToDelete['iconColor']">{{ selectedToDelete['icon'] }}</v-icon> 
        </v-card-title>

        <v-card-text>
          <small>Are you sure you want to delete {{ selectedToDelete['provider'] }} from your connected social accounts?</small>
        </v-card-text>

        <v-card-actions class="d-flex justify-end">
          <v-btn text @click="connectedAccountModal = false">Cancel</v-btn>
          <v-btn text color="red" @click="deleteAccount(selectedToDelete['profile'].entity_id)">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data: () => ({
    connectedAccountModal: false,
    selectedToDelete: null
  }),
  computed: {
    ...mapGetters('auth', [
      'getUserSocialAccounts',
    ]),
    getButtonConfiguration() {
      return (provider) => {
        if (['google', 'linkedin', 'github', 'facebook'].includes(provider)) {
          switch (provider) {
            case 'google': 
              return ['GOOGLE', '#dd4b39', 'mdi-google'];
            case 'github':
              return ['GITHUB', '#171515', 'mdi-github'];
            case 'linkedin':
              return ['LINKEDIN', '#0e76a8', 'mdi-linkedin'];
            case 'facebook':
              return ['FACEBOOK', '#4267B2', 'mdi-facebook'];
          }
        }
      }
    },
  },
  methods: {
    removeConnectedAccount(account, icon, iconColor) {
      this.selectedToDelete = { ...account, icon, iconColor };
      this.connectedAccountModal = true;
    },
    deleteAccount(entity_id) {
      this.$store.dispatch('auth/deleteSocialAccount', { entity_id });
      this.connectedAccountModal = false;
    }
  }
}
</script>

<style>

</style>