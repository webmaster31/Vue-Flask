import axios from '../plugins/axios';
import localService from '../services/localService';

export default {
  namespaced: true,
  state: () => ({
    qr: '',
    recoveryCodes: [],
    userSocialAccounts: [],
  }),
  mutations: {
    setState(state, payload) {
      state[payload.key] = payload.value;
    },
  },
  actions: {
    // 
    // UPDATE PASSWORD
    // 
    async updatePassword({ commit, dispatch }, payload) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.post('/update_password', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
        return true;
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
    // 
    // GET 2FA QR_CODE
    // 
    async getQR({ commit, dispatch }, payload) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.post('/qrcode', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        commit('setState', { key: 'qr', value: data.image });
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
    // 
    // VERIFY AUTH CODE
    // 
    async verifyAuthCode({ commit, dispatch }, payload) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.post('/verify_otp', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        commit('setState', { key: 'recoveryCodes', value: data.data['codes'] });
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
        return true;
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
    // 
    // ENABLE MFA
    // 
    async enableMfa({ commit, dispatch }, payload) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.post('/setup_mfa', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
        const userInfo = {
          ...localService.getItem('userInfo'),
          mfa_enabled: true,
        }
        commit('login/setState', { key: 'currentUser', value: userInfo }, { root: true });
        localService.setItem('userInfo', userInfo);
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
    // 
    // GENERATE RECOVERY CODES
    // 
    async generateRecoveryCodes({ commit, dispatch }) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.post('/recovery_codes');
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        commit('setState', { key: 'recoveryCodes', value: data['data'] });
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
    // 
    // GET CONNECTED SOCIAL ACCOUNTS FOR A USER
    // 
    async getUserSocialAccounts({ commit, dispatch }) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.get('/social');

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }

        commit('setState', { key: 'userSocialAccounts', value: data['login_methods'] });
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
    // 
    // DELETE SOCIAL ACCOUNT FROM USER PROFILE
    // 
    async deleteSocialAccount({ commit, dispatch }, payload) {
      try {
        commit('startLoading', null, { root: true });
        const { data } = await axios.delete(`/social/${payload.entity_id}`);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }

        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
        dispatch('getUserSocialAccounts');
      } catch(e) {
        console.log(e);
      } finally {
        commit('stopLoading', null, { root: true });
      }
    },
  },
  getters: {
    getCurrentQr: state => state.qr,
    getRecoveryCodes: state => state.recoveryCodes,
    getUserSocialAccounts: state =>  state.userSocialAccounts
  }
}