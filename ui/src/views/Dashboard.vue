<template>
  <div>
    <h2>{{ $t("dashboard.title") }}</h2>
    <!-- error message //// -->
    <!-- <div v-if="errorMessage" class="alert alert-danger alert-dismissable">
      <button
        type="button"
        class="close"
        @click="closeErrorMessage()"
        aria-label="Close"
      >
        <span class="pficon pficon-close"></span>
      </button>
      <span class="pficon pficon-error-circle-o"></span>
      {{ errorMessage }}.
    </div> -->
    <div v-if="error.read" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.read }}.
    </div>
    <div v-if="loading.read" class="spinner spinner-lg"></div>
    <div v-else>
      <template v-if="!config.isConnected">
        <!-- connect form -->
        <h3 class="connect-title">
          {{ $t("dashboard.connect_to_ns8_cluster") }}
        </h3>
        <div class="page-description">
          {{ $t("dashboard.connect_description") }}
        </div>
        <form class="form-horizontal" v-on:submit.prevent="connectToCluster">
          <!-- leader node -->
          <div class="form-group">
            <label class="col-sm-2 control-label" for="leader-node">{{
              $t("dashboard.leader_node")
            }}</label>
            <div class="col-sm-5">
              <input
                type="text"
                v-model="config.leaderNode"
                id="leader-node"
                ref="leaderNode"
                class="form-control"
              />
              <span v-if="error.leaderNode" class="help-block">{{
                $t("validation.leader_node_" + error.leaderNode)
              }}</span>
            </div>
          </div>
          <!-- admin username -->
          <div class="form-group">
            <label class="col-sm-2 control-label" for="admin-username">{{
              $t("dashboard.admin_username")
            }}</label>
            <div class="col-sm-5">
              <input
                type="text"
                v-model="config.adminUsername"
                id="admin-username"
                ref="adminUsername"
                class="form-control"
              />
              <span v-if="error.adminUsername" class="help-block">{{
                $t("validation.admin_username_" + error.adminUsername)
              }}</span>
            </div>
          </div>
          <!-- admin password -->
          <div class="form-group">
            <label class="col-sm-2 control-label" for="admin-password">{{
              $t("dashboard.admin_password")
            }}</label>
            <div class="col-sm-5">
              <input
                :type="isPasswordVisible ? 'text' : 'password'"
                v-model="config.adminPassword"
                id="admin-password"
                ref="adminPassword"
                class="form-control"
              />
            </div>
            <div class="col-sm-1">
              <button
                tabindex="-1"
                @click="togglePassword"
                type="button"
                class="btn btn-primary adjust-top-min"
              >
                <span
                  :class="[
                    !isPasswordVisible ? 'fa fa-eye' : 'fa fa-eye-slash',
                  ]"
                ></span>
              </button>
            </div>
          </div>
          <!-- tls verify -->
          <div class="form-group">
            <label class="col-sm-2 control-label" for="tls-verify">{{
              $t("dashboard.tls_verify")
            }}</label>
            <div class="col-sm-2">
              <input
                type="checkbox"
                v-model="config.tlsVerify"
                id="tls-verify"
                class="form-control"
              />
            </div>
          </div>
          <!-- connect button -->
          <div class="form-group">
            <label class="col-sm-2 control-label">
              <div
                v-if="loading.update"
                class="spinner spinner-sm form-spinner-loader adjust-top-loader"
              ></div>
            </label>
            <div class="col-sm-5">
              <button
                class="btn btn-primary"
                type="button"
                :disabled="loading.update"
                @click="connectToCluster"
              >
                {{ $t("dashboard.connect") }}
              </button>
            </div>
          </div>
        </form>
      </template>
      <template v-else>
        <!-- connected to ns8 cluster -->
        <div class="page-description">
          <span
            v-html="
              $t('dashboard.connected_description', {
                leaderNode: config.leaderNode,
              })
            "
          ></span>
          <span>
            <a class="disconnect-link" @click="disconnectFromCluster">
              {{ $t("dashboard.connect_to_different_cluster") }}
            </a>
          </span>
        </div>
        <div id="pf-list-default" class="list-group list-view-pf app-list">
          <div
            v-for="app in config.apps"
            :key="app.name"
            class="list-group-item"
          >
            <div class="list-view-pf-actions">
              <button
                v-if="app.status == 'not_migrated'"
                @click="startMigration(app)"
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
              <button
                v-else-if="app.status == 'migrating'"
                @click="finishMigration(app)"
                class="btn btn-default"
              >
                {{ $t("dashboard.finish_migration") }}
              </button>
              <button
                v-else-if="app.status == 'syncing'"
                disabled
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>

              <button
                v-else-if="app.status == 'migrated'"
                disabled
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
              <div
                v-if="app.status == 'migrating'"
                class="dropdown pull-right dropdown-kebab-pf"
              >
                <button
                  class="btn btn-link dropdown-toggle"
                  type="button"
                  id="dropdownKebabRight"
                  data-toggle="dropdown"
                  aria-haspopup="true"
                  aria-expanded="true"
                >
                  <span class="fa fa-ellipsis-v"></span>
                </button>
                <ul
                  class="dropdown-menu dropdown-menu-right"
                  aria-labelledby="dropdownKebabRight"
                >
                  <li>
                    <a @click="syncData(app)">{{
                      $t("dashboard.sync_data")
                    }}</a>
                  </li>
                </ul>
              </div>
            </div>
            <div class="list-view-pf-main-info">
              <div class="list-view-pf-left">
                <img
                  class="apps-icon"
                  :src="'../' + app.id + '/' + (app.icon || 'logo.png')"
                />
              </div>
              <div class="list-view-pf-body">
                <div class="list-view-pf-description">
                  <div class="list-group-item-heading">
                    {{ app.name }}
                  </div>
                  <div class="list-group-item-text">
                    <div
                      v-if="app.status == 'syncing'"
                      class="spinner spinner-sm form-spinner-loader"
                    ></div>
                    <span
                      v-else-if="app.status == 'migrated'"
                      class="pficon pficon-ok status-icon"
                    ></span>
                    <span
                      v-else-if="app.status == 'migrating'"
                      class="pficon pficon-info status-icon"
                    ></span>
                    <span>{{ $t("dashboard.status_" + app.status) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: "Dashboard",
  props: {},
  data() {
    return {
      isPasswordVisible: false,
      config: {
        isConnected: false,
        tlsVerify: false,
        leaderNode: "leader.ns8.example.org", //// ""
        adminUsername: "admin", //// ""
        adminPassword: "Nethesis,1234", //// ""
        apps: [
          {
            id: "nethserver-nextcloud",
            name: "Nextcloud",
            status: "not_migrated",
          },
          {
            id: "nethserver-mattermost",
            name: "Mattermost",
            status: "not_migrated",
          },
          {
            id: "nethserver-roundcubemail",
            name: "Webmail",
            status: "not_migrated",
          },
        ],
      },
      loading: {
        read: false,
        update: false,
      },
      error: {
        read: "",
        update: "",
        leaderNode: "",
        adminUsername: "",
        adminPassword: "",
      },
    };
  },
  mounted() {
    //// call api
    //// remove mock
    this.config.isConnected = false;
  },
  methods: {
    togglePassword() {
      this.isPasswordVisible = !this.isPasswordVisible;
    },
    connectToCluster() {
      console.log("connectToCluster"); ////

      this.loading.update = true;

      setTimeout(() => {
        ////
        this.loading.update = false;
        this.config.isConnected = true;
      }, 1000);
    },
    startMigration(app) {
      console.log("startMigration", app); ////

      app.status = "syncing";

      setTimeout(() => {
        ////
        app.status = "migrating";
      }, 2000);
    },
    finishMigration(app) {
      console.log("finishMigration", app); ////

      app.status = "syncing";

      setTimeout(() => {
        ////
        app.status = "migrated";
      }, 2000);
    },
    syncData(app) {
      console.log("syncData", app); ////

      app.status = "syncing";

      setTimeout(() => {
        ////
        app.status = "migrating";
      }, 2000);
    },
    disconnectFromCluster() {
      this.config.isConnected = false;
    },
    // readDashboardData() { ////
    //   var ctx = this;
    //   nethserver.exec(
    //     ["nethserver-ns8-migration/dashboard/read"],
    //     { appInfo: "dashboardData" },
    //     null,
    //     function(success) {
    //       var dashboardOutput = JSON.parse(success);
    //       ctx.readDashboardDataSuccess(dashboardOutput);
    //     },
    //     function(error) {
    //       ctx.showErrorMessage(
    //         ctx.$i18n.t("dashboard.error_retrieving_dashboard_data"),
    //         error
    //       );
    //     }
    //   );
    // },
    // readDashboardDataSuccess(dashboardOutput) {
    //   this.dashboardData = dashboardOutput.dashboardData;
    //   this.uiLoaded = true;
    // },
    // showErrorMessage(errorMessage, error) {
    //   console.error(errorMessage, error); /* eslint-disable-line no-console */
    //   this.errorMessage = errorMessage;
    // },
    // closeErrorMessage() {
    //   this.errorMessage = null;
    // },
  },
};
</script>

<style scoped>
.connect-title {
  margin-top: 25px;
}

.page-description {
  margin-bottom: 30px;
}

.app-list {
  margin-top: 20px;
  padding-bottom: 40px;
}

.list-group-item {
  border-bottom: 1px solid #ededed;
}

.disconnect-link {
  margin-left: 5px;
}

.status-icon {
  margin-right: 7px;
  font-size: 16px;
  position: relative;
  top: 2px;
}
</style>
