<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="d-flex justify-center mt-16 pt-16">
        <v-card elevation="8" width="500px">
          <v-card-title class="d-flex justify-center">
            <v-icon size="100" color="#172950">mdi-form-textbox-password</v-icon>
          </v-card-title>

          <v-card-text>
            <v-form ref="form" v-model="valid" lazy-validation>
              <v-text-field
                v-model="password"
                type="password" 
                placeholder="Password" 
                outlined label="Password"
                color="grey"
                :rules="[
                  v => !!v || 'Password is required.', 
                ]"
                required
                class="mb-3"
              />

              <v-text-field 
                v-model="confirmPassword" 
                type="password" 
                placeholder="Confirm Password" 
                outlined label="Confirm Password" 
                color="grey" 
                :rules="[
                  v => !!v || 'Password is required.',
                  v => v === password || 'Passwords do not match.'
                ]"
                required
                class="mb-3"
              />

              <v-btn 
                :disabled="!valid" 
                :loading="isLoading"
                x-large 
                block 
                depressed 
                color="#172950" 
                class="white--text" 
                @click="checkTokenAndUidb"
              >
                Reset Password
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data: () => ({
    showPasswordReset: false,
    password: '',
    confirmPassword: '',
    valid: false,
  }),
  computed: {
    ...mapGetters("login", [
      'isLoading'
    ]),
  },
  methods: {
    checkTokenAndUidb() {
      if (this.$refs.form.validate()) {
        const token = this.$route.params.token;
        const uidb = this.$route.params.uidb;
        this.$store.dispatch('login/resetPassword', { token, uidb, password: this.password });
      }
    }
  },
}
</script>