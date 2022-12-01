<template>
  <v-container>
    <v-row class="d-flex align-center justify-center">
      <v-col cols="12"  class="d-flex flex-column align-center justify-center py-16 mt-16">
        <v-progress-circular :width="3" color="#172950" size="100" indeterminate></v-progress-circular>
        <div v-if="loading" class="mt-10">
          We are confirming your email address
        </div>

        <div v-else class="mt-10">
          Email address confirmed. <br /> Logging you in...
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  computed: {
    loading() {
      return this.$store.getters['login/isLoading'];
    }
  },
  methods: {
    confirmEmail() {
      const token = this.$route.params.token;
      const uidb = this.$route.params.uidb;
      this.$store.dispatch('login/confirmEmail', { token, uidb });
    }
  },
  mounted() {
    this.confirmEmail();
  }
}
</script>

<style>

</style>