<template>
  <div>
    <h2>{{$t('dashboard.title')}}</h2>
      <!-- error message -->
      <div v-if="errorMessage" class="alert alert-danger alert-dismissable">
        <button type="button" class="close" @click="closeErrorMessage()" aria-label="Close">
          <span class="pficon pficon-close"></span>
        </button>
        <span class="pficon pficon-error-circle-o"></span>
        {{ errorMessage }}.
      </div>

      <div v-show="!uiLoaded" class="spinner spinner-lg"></div>
      <div v-show="uiLoaded">
      NS7 2 NS8
      </div>
  </div>
</template>

<script>
export default {
  name: "Dashboard",
  props: {
  },
  mounted() {
    this.readDashboardData()
  },
  data() {
    return {
      uiLoaded: false,
      errorMessage: null,
      dashboardData: {}
    };
  },
  methods: {
    readDashboardData() {
      var ctx = this;
      nethserver.exec(
        ["nethserver-ns8-migration/dashboard/read"],
        { "appInfo": "dashboardData" },
        null,
        function(success) {
          var dashboardOutput = JSON.parse(success);
          ctx.readDashboardDataSuccess(dashboardOutput)
        },
        function(error) {
          ctx.showErrorMessage(ctx.$i18n.t("dashboard.error_retrieving_dashboard_data"), error)
        }
      );
    },
    readDashboardDataSuccess(dashboardOutput) {
      this.dashboardData = dashboardOutput.dashboardData
      this.uiLoaded = true
    },
    showErrorMessage(errorMessage, error) {
      console.error(errorMessage, error) /* eslint-disable-line no-console */
      this.errorMessage = errorMessage
    },
    closeErrorMessage() {
      this.errorMessage = null
    },
  }
};
</script>
