<template>
  <v-container fluid>
    <v-row class="main-bg bg-split">
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="rounded-lg d-flex" width="600px">
          <div class="px-md-10" style="width: 100%;">
            <v-card-title class="d-flex justify-center font-weight-bold">Recover Password</v-card-title>
            <v-card-text>
              <v-form ref="form" v-model="valid" lazy-validation>
                <v-text-field
                  v-model="email"
                  type="email" 
                  placeholder="Email" 
                  outlined label="Email"
                  color="grey"
                  :rules="[
                    v => !!v || 'Email is required.', 
                    v => !v || /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) || 'E-mail must be valid'
                  ]"
                  required
                />

                <v-btn 
                  :disabled="!valid" 
                  :loading="isLoading"
                  large 
                  block 
                  depressed 
                  color="#172950" 
                  class="white--text" 
                  @click="reset"
                >
                  Recover
                </v-btn>
              </v-form>
            </v-card-text>

            <v-card-actions class="d-flex justify-center">
              <div>
                <v-btn small link text @click="$router.push({ path: '/login' })">Login</v-btn>
              </div>

              <v-divider vertical class="mx-1"></v-divider>

              <div>
                <v-btn small link text @click="$router.push({ path: '/signup' })">Create Account</v-btn>
              </div>
            </v-card-actions>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex';
import appSettings from '../../app.settings';


export default {
  data: () => ({
    valid: false,
    email: '',
  }),
  computed: {
    ...mapGetters('login', [
      'isLoading'
    ]),
    appInfo() {
      return appSettings;
    }
  },
  methods: {
    reset() {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('login/forgotPassword', { email: this.email.trim() });
      }
    }
  }
}
</script>

<style scoped>
  .main-bg {
    height: 100vh;
  }
</style>