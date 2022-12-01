<template>
  <v-progress-linear v-if="isLoading" color="#172950" indeterminate></v-progress-linear>
</template>

<script>
export default {
  computed: {
    isLoading() {
      return this.$store.getters.isLoading;
    }
  }
}
</script>