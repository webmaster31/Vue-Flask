import Vue from 'vue';
import Vuex from 'vuex';
import loginModule from './login';
import authModule from './authentication';
import { vm } from '../main';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    appDrawer: false,
    isLoading: false
  },
  mutations: {
    toggleAppDrawer(state) {
      if (state.appDrawer) {
        state.appDrawer = false;
      } else {
        state.appDrawer = true;
      }
    },
    startLoading(state) {
      state.isLoading = true;
    },
    stopLoading(state) {
      state.isLoading = false;
    }
  },
  actions: {
    showMessage({ commit }, payload) {
      return vm.$notify({
        type: payload.messageType,
        title: payload.messageTitle,
        text: payload.message,
      });
    },
  },
  getters: {
    appDrawer: state => state.appDrawer,
    isLoading: state => state.isLoading,
  },
  modules: {
    login: loginModule,
    auth: authModule,
  }
})
