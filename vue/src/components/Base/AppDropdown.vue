<template>
  <v-select
    v-model="defaultValue"
    :items="items" 
    :label="label" 
    color="#172950"
    :menu-props="{ bottom: true, offsetY: true }"
    outlined
    hide-details
    dense 
    @change="handleSelectedItem"
  >
  </v-select>
</template>

<script>
export default {
  props: {
    items: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: () => 'label here'
    }
  },
  data: () => ({
    defaultValue: null
  }),
  methods: {
    handleSelectedItem(item) {
      this.$emit('selected-item', item);
    },
    setDefault() {
      this.defaultValue = this.items[0];
    }
  },
  mounted() {
    this.setDefault();
  }
}
</script>