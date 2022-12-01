<template>
  <v-menu transition="slide-y-transition" offset-y left>
    <template v-slot:activator="{ on, attrs }">
      <v-btn v-bind="attrs" v-on="on" icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
    </template>
    <v-card class="rounded" width="180px">
      <v-list dense nav>
        <v-list-item v-for="(item, index) in items" :key="index" link @click="handleItemClick(item)">
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.name }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
export default {
  data: () => ({
    items: [
      { 
        id: 'logout',
        icon: 'mdi-logout',
        name: 'Logout'
      }
    ]
  }),
  methods: {
    handleItemClick(item) {
      switch (item.id) {
        case 'logout':
          this.$store.dispatch('login/logout');
          break;
      }
    }
  }
}
</script>