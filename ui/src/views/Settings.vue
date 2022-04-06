<template>
  <div>
    <h2>{{$t('settings.title')}}</h2>
    
    <!-- error message -->
    <div v-if="errorMessage" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ errorMessage }}.
    </div>

    <!-- warning message -->
    <div v-if="warningMessage" class="alert alert-warning">
      <span class="pficon pficon-warning-triangle-o"></span>
      {{ warningMessage }}.
    </div>

    <div v-if="!uiLoaded" class="spinner spinner-lg"></div>
    <div v-if="uiLoaded">
    Settings
    </div>
  </div>
</template>

<script>
export default {
  name: "Settings",
  mounted() {
    this.getConfig()
  },
  data() {
    return {
      uiLoaded: false,
    }
  },
  methods: {
    getConfig() {
      var ctx = this;
      nethserver.exec(
        ["nethserver-ns8-migration/configuration/read"],
        { "appInfo": "token" },
        null,
        function(success) {
          var data = JSON.parse(success);
        },
        function(error) {
          ctx.showErrorMessage(ctx.$i18n.t("settings.error_retrieving_token_from_file"), error)
        }
      );
    },
  }
};
</script>

<style scoped>
.margin-top-20 {
  margin-top: 20px
}

.no-padding {
  padding: 0px
}

.adjust-top-loader {
    margin-top: -4px;
}
</style>
