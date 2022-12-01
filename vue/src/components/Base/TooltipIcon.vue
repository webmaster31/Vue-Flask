<template>
  <v-tooltip left color="#172950">
    <template v-slot:activator="{ on, attrs }">
      <v-btn large icon v-bind="attrs" v-on="on" color="#172950">
        <v-icon>
          mdi-{{ icon }}
        </v-icon>
      </v-btn>
    </template>
    <span>{{ tooltip }}</span>
  </v-tooltip>
</template>

<script>
export default {
  props: {
    icon: {
      type: String,
      required: true,
    },
    tooltip: {
      type: String,
      required: false,
      default: () => 'Your Tooltip'
    }
  }
}
</script>