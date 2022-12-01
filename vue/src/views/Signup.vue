<template>
  <v-container fluid>
    <v-row class="main-bg">
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="rounded-lg d-flex" width="700px">
          <div class="px-md-10" style="width: 100%;"> 
            <v-card-title class="d-flex justify-center font-weight-bold">Create Account</v-card-title>
            <v-card-text >
              <v-form ref="form" v-model="valid" lazy-validation>
                <v-text-field
                  v-model="firstname"
                  type="text" 
                  placeholder="Firstname" 
                  outlined label="Firstname"
                  color="grey"
                  :rules="[
                    v => !!v || 'Firstname is required.', 
                    v => v.length > 2 || 'Not valid.'
                  ]"
                  required
                />

                <v-text-field 
                  v-model="lastname"
                  type="text" 
                  placeholder="Lastname" 
                  outlined label="Lastname" 
                  color="grey"
                  :rules="[
                    v => !!v || 'Lastname is required.'
                  ]"
                  required
                />

                <v-text-field 
                  v-model="email"
                  type="email" 
                  placeholder="Email" 
                  outlined label="Email" 
                  color="grey"
                  :rules="[
                    v => !!v || 'Email is required.',
                    v => !v || /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) || 'E-mail must be valid',
                  ]"
                  required
                />

                <v-text-field 
                  v-model="password"
                  type="password" 
                  placeholder="Password" 
                  outlined label="Password" 
                  color="grey"
                  :rules="[
                    v => !!v || 'Password is required.'
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
                  @click="signup"
                >
                  Signup
                </v-btn>
              </v-form>
            </v-card-text>

            <v-card-actions class="d-flex justify-center">
              <div>
                <v-btn small link text @click="$router.push({ path: '/login' })">Back to Login</v-btn>
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
import appSettings from '../../app.settings.js';

export default {
  data: () => ({
    valid: false,
    firstname: '',
    lastname: '',
    email: '',
    password: '',
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
    signup() {
      const payload = {
        login_method: "signup",
        first_name: this.firstname,
        last_name: this.lastname,
        email: this.email.trim(),
        password: this.password
      }
      if (this.$refs.form.validate()) {
        this.$store.dispatch('login/signup', payload);
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