import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify';
import api from './plugins/axios';
import GoogleAuth from './config/googleAuth';
import Notifications from 'vue-notification'

// Constants
import { googleAuthSettings } from './config/constants'; 
import { initFbsdk } from './config/facebookAuth';

initFbsdk();

const gAuthOption = {
  ...googleAuthSettings
}

Vue.config.productionTip = false;
Vue.use(GoogleAuth, gAuthOption);
Vue.use(Notifications)
Vue.prototype.$axios = api;

const vm = new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

export { vm }