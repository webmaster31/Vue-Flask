import axios from '../plugins/axios';
import localService from '../services/localService';
import { vm } from '../main';

export default {
  namespaced: true,
  state: () => ({
    isLoading: false,
    currentUser: {},
    isLoggedIn: false,
    loginType: {},
  }),
  mutations: {
    setState(state, payload) {
      state[payload.key] = payload.value;
    },
    resetState(state) {
      state.currentUser = {};
      state.loginType = {};
      state.isLoggedIn = false;
    }
  },
  actions: {
    // 
    // USED FOR LOGGING IN A USER
    // 
    async login({ commit, dispatch}, payload) {
      const loginType = {
        type: 'normal',
        provider: 'signup',
      };

      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/login', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }

        if (data.user.verified === 0) {
          dispatch('showMessage', { message: 'Please visit your email and verify the account first', messageType: 'error', messageTitle: 'Account not verified' }, { root: true });
          return { showResendLink: true }
        }

        if (data.user.mfa_enabled) {
          return { showMfa: true, loginType }
        }

        commit('setState', { key: 'currentUser', value: data['user'] });
        commit('setState', { key: 'isLoggedIn', value: true });
        commit('setState', { key: 'loginType', value: loginType });
        localService.setItem('userInfo', { ...data['user'], full_name: data['user']['first_name'] + ' ' + data['user']['last_name'] });
        localService.setItem('token', data['user']['access_token']);
        localService.setItem('loginType', loginType);
        vm.$router.push({ path: '/dashboard' });
      } catch (e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // USED FOR CREATING A NEW ACCOUNT
    // 
    async signup({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/signup', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
        vm.$router.push({ path: '/login' });
      } catch (e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // USED FOR LOGGING-OUT A USER
    // 
    async logout({ commit }) {
      try {
        const { data } = await axios.post('/logout');
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        commit('resetState');
        localService.removeItem('token');
        localService.removeItem('userInfo');
        localService.removeItem('loginType');
        vm.$router.push({ path: '/login' });
      } catch (e) {
        console.log(e);
      } finally { }
    },
    // 
    // USED TO RESET PASSWORD FOR A ACCOUNT
    // 
    async forgotPassword({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/forgot_password', payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
        vm.$router.push({ path: '/login', query: { email: payload.email, from: 'forgot-password'} });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // USED TO CONFIRM EMAIL
    // 
    async confirmEmail({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post(`/verify/${payload.token}/${payload.uidb}`);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        setTimeout(() => {
          commit('setState', { key: 'currentUser', value: data['user'] });
          commit('setState', { key: 'isLoggedIn', value: true });
          localService.setItem('userInfo', { ...data['user'], full_name: data['user']['first_name'] + ' ' + data['user']['last_name'] });
          localService.setItem('token', data['user']['access_token']);
          vm.$router.push({ path: '/dashboard' });
        }, 3000);
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // RESEND CONFIRMATION LINK
    // 
    async resendEmail({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post(`/resend_confirmation`, payload);
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // RESET THE PASSWORD
    // 
    async resetPassword({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post(`/reset_password/${payload.token}/${payload.uidb}`, { password: payload.password });
        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        vm.$router.push({ path: '/login' });
        dispatch('showMessage', { ...data, messageType: 'success', messageTitle: 'Success' }, { root: true });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // MFA LOGIN
    // 
    async loginMfa({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/login_mfa', payload);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        
        commit('setState', { key: 'currentUser', value: data['user'] });
        commit('setState', { key: 'isLoggedIn', value: true });
        localService.setItem('userInfo', { ...data['user'], full_name: data['user']['first_name'] + ' ' + data['user']['last_name'] });
        localService.setItem('token', data['user']['access_token']);
        vm.$router.push({ path: '/dashboard' });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // LOGIN USING A RECOVERY CODE
    // 
    async loginUsingRecovery({ commit, dispatch }, payload) {
      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/verify_recovery_code', payload);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        
        commit('setState', { key: 'currentUser', value: data['user'] });
        commit('setState', { key: 'isLoggedIn', value: true });
        localService.setItem('userInfo', { ...data['user'], full_name: data['user']['first_name'] + ' ' + data['user']['last_name'] });
        localService.setItem('token', data['user']['access_token']);
        vm.$router.push({ path: '/dashboard' });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // LOGIN USING SOCIAL AUTH (GOOGLE)
    // 
    async connectGoogleToAccount({ commit, dispatch }, payload) {
      const loginType = {
        type: 'social',
        provider: 'google',
      };

      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/social/google', payload);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }
        if (data.user.mfa_enabled) {
          return { 
            showMfa: true,
            email: data?.auth?.email,
            loginType
          }
        }

        commit('setState', { key: 'currentUser', value: { ...data.auth, ...data.user } });
        commit('setState', { key: 'isLoggedIn', value: true });
        commit('setState', { key: 'loginType', value: loginType });
        localService.setItem('userInfo', { ...data.auth, ...data.user, full_name: data['auth']['user_name'].split(' ')[0] + ' ' + data['auth']['user_name'].split(' ')[1] });
        localService.setItem('token', data['user']['access_token']);
        localService.setItem('loginType', loginType);
        vm.$router.push({ path: '/dashboard' });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // LOGIN USING GITHUB
    // 
    async connectGithubToAccount({ commit, dispatch }, payload) {
      const loginType = {
        type: 'social',
        provider: 'github',
      };

      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/social/github', payload);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }

        if (data.user.mfa_enabled) {
          return { showMfa: true, email: data?.auth?.email, loginType }
        }

        commit('setState', { key: 'currentUser', value: { ...data.auth, ...data.user } });
        commit('setState', { key: 'isLoggedIn', value: true });
        commit('setState', { key: 'loginType', value: loginType });
        localService.setItem('userInfo', { ...data.auth, ...data.user, full_name: data['auth']['user_name'].split(' ')[0] + ' ' + data['auth']['user_name'].split(' ')[1] });
        localService.setItem('token', data['user']['access_token']);
        localService.setItem('loginType', loginType);
        vm.$router.push({ path: '/dashboard' });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // LOGIN USING LINKEDIN
    // 
    async connectLinkedInToAccount({ commit, dispatch }, payload) {
      const loginType = {
        type: 'social',
        provider: 'linkedin',
      };

      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/social/linkedin', payload);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }

        if (data.user.mfa_enabled) {
          return { showMfa: true, email: data?.auth?.email, loginType }
        }

        commit('setState', { key: 'currentUser', value: { ...data.auth, ...data.user } });
        commit('setState', { key: 'isLoggedIn', value: true });
        commit('setState', { key: 'loginType', value: loginType });
        localService.setItem('userInfo', { ...data.auth, ...data.user, full_name: data['auth']['user_name'].split(' ')[0] + ' ' + data['auth']['user_name'].split(' ')[1] });
        localService.setItem('token', data['user']['access_token']);
        localService.setItem('loginType', loginType);
        vm.$router.push({ path: '/dashboard' });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
    // 
    // LOGIN USING Facebook
    // 
    async connectFacebookToAccount({ commit, dispatch }, payload) {
      const loginType = {
        type: 'social',
        provider: 'facebook',
      };

      try {
        commit('setState', { key: 'isLoading', value: true });
        const { data } = await axios.post('/social/facebook', payload);

        if (!data.success) {
          return dispatch('showMessage', { ...data, messageType: 'error', messageTitle: 'Error' }, { root: true });
        }

        if (data.user.mfa_enabled) {
          return { showMfa: true, email: data?.auth?.email, loginType }
        }

        commit('setState', { key: 'currentUser', value: { ...data.auth, ...data.user } });
        commit('setState', { key: 'isLoggedIn', value: true });
        commit('setState', { key: 'loginType', value: loginType });
        localService.setItem('userInfo', { ...data.auth, ...data.user, full_name: data['auth']['user_name'].split(' ')[0] + ' ' + data['auth']['user_name'].split(' ')[1] });
        localService.setItem('token', data['user']['access_token']);
        localService.setItem('loginType', loginType);
        vm.$router.push({ path: '/dashboard' });
      } catch(e) {
        console.log(e);
      } finally {
        commit('setState', { key: 'isLoading', value: false });
      }
    },
  },
  getters: {
    currentUser: state => state.currentUser,
    isLoading: state => state.isLoading,
    isLoggedIn: state => state.isLoggedIn,
    loginType: state => state.loginType,
  }
}