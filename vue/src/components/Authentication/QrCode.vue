<template>
  <v-card outlined>
    <v-card-title>
      <div class="d-flex align-center">
        Enable 2-Factor Authentication
      </div>
    </v-card-title>

    <v-card-text>
      <v-form ref="form" v-model="valid" lazy-validation v-if="loginTypeInfo.type === 'normal'">
        <v-text-field
          v-model="password"
          type="password" 
          placeholder="Password" 
          outlined label="Enter your password"
          color="#172950" 
          dense
          :rules="[
            v => !!v || 'Password is required.'
          ]"
          required
        />

        <v-btn 
          :disabled="!valid || disableVerifyButton" 
          block 
          depressed 
          color="#172950" 
          class="white--text" 
          @click="getQrCode"
        >
          Verify
        </v-btn>
      </v-form>

      <v-expand-transition>
        <v-card class="mt-3" flat v-show="getCurrentQr">
          <v-btn 
            :disabled="!valid" 
            block 
            depressed 
            color="#172950" 
            class="white--text mb-3" 
            @click="generateAuthCodes"
          >
            Generate Auth Codes
          </v-btn>

          <div class="font-weight-medium justified">Please scan the below qr code using 
            <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=en_IN&gl=US">google autheticator</a> 
            to activate 2-factor authetication for your account.
          </div>

          <div class="text-center">
            <img class="fadeIn"  :src="'data:image/png;base64,' + getCurrentQr" />
          </div>

          <v-form ref="qrform" v-model="qrValid" lazy-validation>
            <v-text-field
              v-model="authCode"
              type="password" 
              placeholder="Enter auth code from google authenticator" 
              outlined label="Auth Code"
              color="#172950" 
              :rules="[
                v => !!v || 'Auth code is required to setup mfa.',
                v =>  v && v.length === 6 || 'Please enter a valid auth code.'
              ]"
              required
              dense
            />

            <v-btn 
              :disabled="!qrValid" 
              block 
              depressed 
              color="#172950" 
              class="white--text" 
              @click="sendAuthCode"
            >
              Activate
            </v-btn>
          </v-form>
        </v-card>
      </v-expand-transition>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data: () => ({
    valid: false,
    password: '',
    loginType: 'signup',
    qrValid: false,
    authCode: '',
    disableVerifyButton: false,
  }),
  watch: {
    getCurrentQr: function(val) {
      if (val) {
        this.disableVerifyButton = true;
      }
    },
    getRecoveryCodes: function(val) {
      if (val) {
        this.resetValues();
        this.$emit('show-recovery-codes');
      }
    }
  },
  computed: {
    isLoading() {
      return this.$store.getters.isLoading;
    },
    ...mapGetters('auth', [
      'getCurrentQr',
      'getRecoveryCodes',
    ]),
    userInfo() {
      return this.$store.getters['login/currentUser'];
    },
    loginTypeInfo() {
      return this.$store.getters['login/loginType'];
    }
  },
  methods: {
    generateAuthCodes() {
      this.$store.dispatch('auth/generateRecoveryCodes');
    },
    getQrCode() {
      if (this.$refs.form.validate()) {
        if (this.userInfo.mfa_enabled) {
          return this.$emit('show-confirmation-dialog');
        }
        this.sendQrDataToServer();
      }
    },
    sendQrDataToServer() {
      this.$store.dispatch('auth/getQR', { password: this.password, login_type: this.loginType });
    },  
    sendAuthCode() {
      if (this.$refs.qrform.validate()) {
        this.$store.dispatch('auth/verifyAuthCode', { otp: this.authCode })
        .then(res => {
          if (res) {
            this.valid = true;
          }
        });
      }
    },
    enableMfa() {
      this.$store.dispatch('auth/enableMfa', { mfa_enabled: true, otp: this.authCode })
      .then((res) => {
        if (res) this.enableMfa();
      });
    },
    checkLoginType() {
      if (this.loginTypeInfo.type === 'social') {
        this.loginType = this.loginTypeInfo.type;
        return this.sendQrDataToServer();
      }
    },
    resetValues() {
      if (this.loginTypeInfo.type === 'normal') {
        this.$refs.form.reset();
        this.disableVerifyButton = false;
        this.$store.commit('authsetState', { key: 'qr', value: '' });
      }
      this.$refs.qrform.reset(); 
    }
  },
  mounted() {
    this.checkLoginType();
  }
}
</script>

<style scoped>
  .fadeIn {
    opacity: 1;
    width: 60%;
    transition: width 1.5s, height 1.5s, opacity 1.5s 1.5s;
  }
</style>