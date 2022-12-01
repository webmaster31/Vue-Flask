<template>
  <v-card outlined>
    <v-card-title>
      <div class="d-flex align-center text-h6">
        Update Password
      </div>
    </v-card-title>
    
    <v-card-text>
      <v-form ref="form" v-model="valid" lazy-validation class="mt-4">
        <v-text-field
          v-model="existingPassword"
          type="password" 
          placeholder="Enter Your Current Password" 
          outlined label="Current Password"
          color="#172950"
          :rules="[
            v => !!v || 'Current Password is required.', 
          ]"
          required
          dense
        />

        <v-text-field
          v-model="newPassword"
          type="password" 
          placeholder="Enter Your New Password" 
          outlined label="New Password"
          color="#172950"
          :rules="[
            v => !!v || 'New Password is required.', 
          ]"
          required
          dense
        />

        <v-btn 
          :disabled="!valid" 
          block 
          depressed 
          color="#172950" 
          class="white--text" 
          @click="updatePassword"
        >
          Update Password
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data: () => ({
    existingPassword: '',
    newPassword: '',
    valid: false,
  }),
  computed: {
    isLoading() {
      return this.$store.getters.isLoading;
    },
  },
  methods: {
    updatePassword() {
      if (this.$refs.form.validate()) {
        const payload = {
          existing_password: this.existingPassword,
          new_password: this.newPassword
        };
        this.$store.dispatch('auth/updatePassword', payload)
        .then(res => {
          if (res) {
            this.$refs.form.reset();
          }
        })
      }
    }
  }
}
</script>
