<template>
  <v-container fluid>
    <v-row class="main-bg">
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="rounded-lg d-flex">
          <div class="px-md-10"> 
            <v-card-title class="d-flex justify-center font-weight-bold">Login</v-card-title>
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
                  @click="login"
                >
                  Login
                </v-btn>

                <v-btn 
                  v-if="showResendLink"
                  :loading="isLoading"
                  large 
                  block 
                  depressed 
                  color="#172950" 
                  class="white--text mt-2" 
                  @click="resendConfirmationLink"
                >
                  Resend Confirmation Link
                </v-btn>
              </v-form>

              <div class="d-flex justify-space-between mt-6 flex-wrap" v-if="appInfo.showSocialLoginButtons">
                <div class="d-flex justify-center custom-width">
                  <v-btn large depressed block outlined color="#4267B2" @click="loginWithFacebook">
                    <v-icon color="#4267B2" class="mr-2">mdi-facebook</v-icon>
                    Facebook
                  </v-btn>
                </div>

                <div class="d-flex justify-center custom-width">
                  <v-btn large depressed block outlined color="#DB4437" @click="loginWithGoogle">
                    <v-icon color="#DB4437" class="mr-2">mdi-google</v-icon>
                    Google
                  </v-btn>
                </div>

                <div class="d-flex justify-center custom-width mt-2">
                  <v-btn large depressed block outlined color="#171515" @click="loginWithGithub">
                    <v-icon color="#171515" class="mr-2">mdi-github</v-icon>
                    Github
                  </v-btn>
                </div>

                <div class="d-flex justify-center custom-width mt-2">
                  <v-btn large depressed block outlined color="#0e76a8" @click="loginWithLinkedIn">
                    <v-icon color="#0e76a8" class="mr-2">mdi-linkedin</v-icon>
                    Linkedin
                  </v-btn>
                </div>
              </div>
            </v-card-text>

            <v-card-actions class="d-flex justify-center">
              <div>
                <v-btn small link text @click="$router.push({ path: '/signup' })">Create account</v-btn>
              </div>

              <v-divider vertical class="mx-1"></v-divider>

              <div>
                <v-btn small link text @click="$router.push({ path: '/reset-password' })">Forgot password</v-btn>
              </div>
            </v-card-actions>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- DIALOGS -->
    <v-dialog v-model="mfa_dialog" persistent width="600px">
      <v-card>
        <v-card-title class="d-flex flex-column justify-center align-center">
          <v-icon x-large color="#172950">mdi-shield-lock-open</v-icon>
          Authentication Required
        </v-card-title>

        <v-card-text>
          <div class="text-center mb-6">Please open the app which you used to setup the two-factor authentication and type the code in here to proceed with the login.</div>
          <v-form ref="twoFactorForm" v-model="twoFactor" lazy-validation class="mt-6">
            <v-text-field 
              v-model="authCode"
              type="password" 
              placeholder="Auth Code" 
              outlined label="Auth Code" 
              color="grey"
              :rules="[
                v => !!v || 'Auth code is required.',
                v => v.length === 6 || 'Auth code is invalid.'
              ]"
              required
            />

            <v-btn 
              :disabled="!twoFactor || (recoveryCode.length ? true : false)" 
              :loading="isLoading"
              x-large 
              block 
              depressed 
              color="#172950" 
              class="white--text" 
              @click="loginUsingMfa"
            >
              Verify & Login
            </v-btn>  
          </v-form>

          <div class="separator" style="border-bottom: 1px solid lightgray; height: 12px">
            <div class="or-text">OR</div>
          </div>

          <v-text-field 
            v-model="recoveryCode"
            type="password" 
            placeholder="Recovery Code" 
            outlined label="Recovery Code" 
            color="grey"
            required
            class="mt-3"
          />

          <v-btn 
            :disabled="!recoveryCode"
            :loading="isLoading"
            x-large 
            block 
            depressed 
            color="#172950" 
            class="white--text" 
            @click="loginUsingRecoveryCode"
          >
            Login Using Recovery Code
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex';
import localService from '../services/localService';
import appSettings from '../../app.settings.js';

export default {
  data: () => ({
    valid: false,
    email: '',
    password: '',
    showResendLink: false,
    mfa_dialog: false,
    twoFactor: false,
    authCode: '',
    recoveryCode: '',
    mfaEmail: '',
  }),
  computed: {
    ...mapGetters("login", [
      'isLoading'
    ]),
    appInfo() {
      return appSettings;
    }
  },
  watch: {
    email: function(val) {
      if (val.length > 0) {
        this.$router.replace({ path: `/login?email=${val}` });
      } else {
        this.$router.replace({ path: '/login' });
      }
    },
  },
  methods: {
    loginWithGoogle () {
      this.$gAuth.signIn()
      .then(GoogleUser => {
        this.setInfoForUser(GoogleUser, 'google');
      })
      .catch(error => {
        this.$notify({
          type: 'warn',
          title: 'Google Authentication',
          text: this.getGoogleAuthErrorMessages(error)
        });
      })
    },
    loginWithFacebook() {
      window.FB.login(response => {
        if (response.authResponse === null && response.status === 'unknown') {
          return this.$notify({
            type: 'warn',
            title: 'Facebook Authentication',
            text: 'Something went wrong with facebook authetication.'
          });
        }
        console.log(response);
        this.proceedWithFacebookLogin(response);
      }, 
      { 
        scope: 'public_profile,email',
        return_scopes: true
      })
    },
    async proceedWithFacebookLogin(response) {
      const data = await this.getUsersFacebookProfile(response);

      let payload = { 
        ...response.authResponse,
        name: data.name,
        email: data.email 
      };
      delete payload.signedRequest
      delete payload.graphDomain
      
      this.$store.dispatch('login/connectFacebookToAccount', payload).then((res) => {
        if (res && res.showResendLink) {
          return this.showResendLink = true;
        }

        if (res && res.showMfa) {
          if (res?.loginType) {
            localService.setItem('loginType', res.loginType);
          }
          return this.mfa_dialog = true;
        }
      });
    },
    async getUsersFacebookProfile(response) {
      const endpoint = 'https://graph.facebook.com/me';
      const fields = 'name,email';
      const apiUrl = `${endpoint}?fields=${fields}&access_token=${response.authResponse.accessToken}`;
      const usersData = await this.$axios.get(apiUrl);
      return { ...usersData.data, token: response.authResponse.accessToken };
    },
    setInfoForUser(data, type) {      
      this.$store.dispatch('login/connectGoogleToAccount', 
        { idtoken: data.getAuthResponse()['id_token'] }
      ).then((res) => {
        if (res && res.showMfa) {
          return this.userIsMfa(res);
        }
      });
    },
    getGoogleAuthErrorMessages(error) {
      if (!error) {
        return 'Something went wrong please try again!'
      }

      try {
        if (error?.error.includes('popup_closed_by_user')) { 
          return 'Authentication popup was closed!'
        }
      } catch (e) {
        console.log(e);
      } 
      
    },
    getLoginPayload() {
      return {
        email: this.email.trim(),
        password: this.password
      }
    },
    login() {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('login/login', this.getLoginPayload()).then((res) => {
          if (res && res.showResendLink) {
            return this.showResendLink = true;
          }

          if (res && res.showMfa) {
            if (res?.loginType) {
              localService.setItem('loginType', res.loginType);
            }
            return this.mfa_dialog = true;
          }
        });
      }
    },
    userIsMfa(res) {
      if (res?.loginType) {
        localService.setItem('loginType', res.loginType);
      }
      this.email = res.email;
      this.mfaEmail = res.email;
      return this.mfa_dialog = true;
    },
    checkForQueryParams() {
      if (this.$route.query.email && this.$route.query.from === 'forgot-password') {
        this.email = this.$route.query.email;
        this.password = '';
      }

      if (this.$route.query.code && this.$route.query.state.includes('github')) {
        this.$store.dispatch('login/connectGithubToAccount', { code: this.$route.query.code })
        .then(res => {
          if (res && res.showMfa) {
            return this.userIsMfa(res);
          }
        });
      }

      if (this.$route.query.code && this.$route.query.state.includes('linkedin')) {
        this.$store.dispatch('login/connectLinkedInToAccount', { code: this.$route.query.code })
        .then(res => {
          if (res && res.showMfa) {
            return this.userIsMfa(res);
          }
        });
      }
    },
    resendConfirmationLink() {
      if (this.email) {
        this.$store.dispatch('login/resendEmail', { email: this.email });
      }
    },
    loginUsingMfa() {
      if (this.$refs.twoFactorForm.validate()) {
        this.$store.dispatch('login/loginMfa', { email: this.mfaEmail ? this.mfaEmail : this.email, otp: this.authCode })
      }
    },
    loginUsingRecoveryCode() {
      if (this.recoveryCode.length) {
        this.$store.dispatch('login/loginUsingRecovery', { email: this.email, recovery_code: this.recoveryCode });
      }
    },
    loginWithGithub() {
      const endpoint = 'https://github.com/login/oauth/authorize?';
      const clientId = process.env.VUE_APP_GITHUB_CLIENT_ID;
      const stateName = process.env.VUE_APP_GITHUB_STATE_NAME;
      const scopes = 'user';
      window.location.href = `${endpoint}response_type=code&client_id=${clientId}&state=${stateName}&scope=${scopes}`;
    },
    loginWithLinkedIn() {
      const endpoint = 'https://www.linkedin.com/oauth/v2/authorization?';
      const clientId = process.env.VUE_APP_LINKEDIN_CLIENT_ID;
      const stateName = process.env.VUE_APP_LINKEDIN_STATE_NAME;
      const scopes = 'r_liteprofile%20r_emailaddress';
      const redirect_uri = process.env.VUE_APP_LINKEDIN_REDIRECT_URI;
      window.location.href = `${endpoint}response_type=code&client_id=${clientId}&state=${stateName}&scope=${scopes}&redirect_uri=${redirect_uri}`;
    }
  },
  mounted() {
    this.checkForQueryParams();
  }
}
</script>

<style scoped lang="scss">
  .main-bg {
    height: 100vh;
  }

  .custom-width {
    width: 48%
  }
</style>