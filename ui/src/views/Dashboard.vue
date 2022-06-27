<template>
  <div>
    <h2>{{ $t("dashboard.title") }}</h2>
    <div v-if="error.connectionRead" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.connectionRead }}
    </div>
    <div v-if="loading.connectionRead" class="spinner spinner-lg"></div>
    <div v-else>
      <template v-if="!config.isConnected">
        <!-- connect form -->
        <h3 class="connect-title">
          {{ $t("dashboard.connect_to_ns8_cluster") }}
        </h3>
        <div class="page-description">
          {{ $t("dashboard.connect_description") }}
        </div>
        <form class="form-horizontal" v-on:submit.prevent="connectionValidate">
          <!-- leader node -->
          <div :class="['form-group', { 'has-error': error.leaderNode }]">
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
          <div :class="['form-group', { 'has-error': error.adminUsername }]">
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
          <div :class="['form-group', { 'has-error': error.adminPassword }]">
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
              <span v-if="error.adminPassword" class="help-block">{{
                $t("validation.admin_password_" + error.adminPassword)
              }}</span>
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
                v-if="loading.connectionUpdate"
                class="spinner spinner-sm form-spinner-loader adjust-top-loader"
              ></div>
            </label>
            <div class="col-sm-5">
              <button
                class="btn btn-primary"
                type="button"
                :disabled="loading.connectionUpdate"
                @click="connectionValidate"
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
            <a class="disconnect-link" @click="disconnectFromCluster"
              >{{ $t("dashboard.connect_to_different_cluster") }}
            </a>
          </span>
        </div>
        <div id="pf-list-default" class="list-group list-view-pf app-list">
          <div v-for="app in apps" :key="app.name" class="list-group-item">
            <div class="list-view-pf-actions">
              <button
                v-if="app.status == 'not_migrated'"
                @click="startMigration(app)"
                :disabled="loading.migrationUpdate"
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
              <button
                v-else-if="app.status == 'migrating'"
                @click="finishMigration(app)"
                :disabled="loading.migrationUpdate"
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
                    <a
                      @click="syncData(app)"
                      :disabled="loading.migrationUpdate"
                      >{{ $t("dashboard.sync_data") }}</a
                    >
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
                      class="pficon pficon-maintenance status-icon"
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
        leaderNode: "",
        adminUsername: "",
        adminPassword: "",
      },
      apps: [
        // { ////
        //   id: "nethserver-nextcloud",
        //   name: "Nextcloud",
        //   status: "not_migrated",
        // },
        // {
        //   id: "nethserver-mattermost",
        //   name: "Mattermost",
        //   status: "not_migrated",
        // },
        // {
        //   id: "nethserver-roundcubemail",
        //   name: "Webmail",
        //   status: "not_migrated",
        // },
      ],
      loading: {
        connectionRead: false,
        connectionUpdate: false,
        migrationRead: false,
        migrationUpdate: false,
      },
      error: {
        connectionRead: "",
        connectionUpdate: "",
        migrationRead: "",
        migrationUpdate: "",
        leaderNode: "",
        adminUsername: "",
        adminPassword: "",
      },
    };
  },
  mounted() {
    this.connectionRead();

    //// remove mock
    // this.config.isConnected = false;
  },
  methods: {
    togglePassword() {
      this.isPasswordVisible = !this.isPasswordVisible;
    },
    // connectToCluster() { ////
    //   console.log("connectToCluster"); ////

    //   this.loading.connectionUpdate = true;

    //   setTimeout(() => {
    //     ////
    //     this.loading.connectionUpdate = false;
    //     this.config.isConnected = true;
    //   }, 1000);
    // },
    startMigration(app) {
      console.log("startMigration", app); ////

      this.migrationUpdate(app, "start");

      // app.status = "syncing";

      // setTimeout(() => {
      //   ////
      //   app.status = "migrating";
      // }, 2000);
    },
    finishMigration(app) {
      console.log("finishMigration", app); ////

      this.migrationUpdate(app, "finish");

      // app.status = "syncing"; ////

      // setTimeout(() => {
      //   ////
      //   app.status = "migrated";
      // }, 2000);
    },
    syncData(app) {
      console.log("syncData", app); ////

      this.migrationUpdate(app, "sync");

      // app.status = "syncing"; ////

      // setTimeout(() => {
      //   ////
      //   app.status = "migrating";
      // }, 2000);
    },
    disconnectFromCluster() {
      this.config.isConnected = false; ////
    },
    connectionRead() {
      const context = this;
      context.loading.connectionRead = true;
      nethserver.exec(
        ["nethserver-ns8-migration/connection/read"],
        {},
        null,
        function(success) {
          const output = JSON.parse(success);
          context.connectionReadSuccess(output);
        },
        function(error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_connection_data"
          );
          console.error(
            errorMessage,
            error
          ); /* eslint-disable-line no-console */
          context.error.connectionRead = errorMessage;
        }
      );
    },
    connectionReadSuccess(output) {
      console.log("connectionReadSuccess", output); ////

      const agentStatus = output.configuration.agent.props.status; ////
      this.config.isConnected = agentStatus == "enabled";
      const ns8Config = output.configuration.ns8.props;
      this.config.leaderNode = ns8Config.Host;
      this.config.adminUsername = ns8Config.User;
      this.config.adminPassword = ns8Config.Password;
      this.config.tlsVerify = ns8Config.TLSVerify == "enabled";
      this.loading.connectionRead = false;

      if (this.config.isConnected) {
        this.migrationRead();
      } else {
        this.$nextTick(() => {
          this.$refs.leaderNode.focus();
        });
      }

      //// remove mock
      // this.config.leaderNode = "192.168.122.183";
      // this.config.adminUsername = "admin";
      // this.config.adminPassword = "Nethesis,12345";
    },
    connectionValidate() {
      this.error.leaderNode = "";
      this.error.adminUsername = "";
      this.error.adminPassword = "";
      this.error.leaderNode = "";
      this.loading.connectionUpdate = true;

      var validateObj = {
        Host: this.config.leaderNode,
        User: this.config.adminUsername,
        Password: this.config.adminPassword,
        TLSVerify: this.config.tlsVerify ? "enabled" : "disabled",
      };

      const context = this;
      nethserver.exec(
        ["nethserver-ns8-migration/connection/validate"],
        validateObj,
        null,
        function(success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          context.connectionValidateSuccess(validateObj);
        },
        function(error, data) {
          context.connectionValidateError(error, data);
        }
      );
    },
    connectionValidateError(error, data) {
      console.log("connectionValidateError", error, data); ////

      this.loading.connectionUpdate = false;
      const errorData = JSON.parse(data);

      for (const e in errorData.attributes) {
        const attr = errorData.attributes[e];
        const param = attr.parameter;

        if (param === "Host") {
          this.error.leaderNode = attr.error;
          this.$refs.leaderNode.focus();
        } else if (param === "User") {
          this.error.adminUsername = attr.error;
          this.$refs.adminUsername.focus();
        } else if (param === "Password") {
          this.error.adminPassword = attr.error;
          this.$refs.adminPassword.focus();
        }
      }
    },
    connectionValidateSuccess(validateObj) {
      console.log("connectionValidateSuccess"); ////

      nethserver.notifications.success = this.$i18n.t(
        "dashboard.connection_successful"
      );
      nethserver.notifications.error = this.$i18n.t(
        "dashboard.connection_failed"
      );
      const context = this;
      nethserver.exec(
        ["nethserver-ns8-migration/connection/update"],
        validateObj,
        function(stream) {
          console.info("ns8-migration-update", stream);
        },
        function(success) {
          context.loading.connectionUpdate = false;
          context.connectionRead();
        },
        function(error) {
          console.error(error);
          context.loading.connectionUpdate = false;
        }
      );
    },
    migrationRead() {
      const context = this;
      context.loading.migrationRead = true;
      nethserver.exec(
        ["nethserver-ns8-migration/migration/read"],
        {},
        null,
        function(success) {
          const output = JSON.parse(success);
          context.migrationReadSuccess(output);
        },
        function(error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_migration_data"
          );
          console.error(
            errorMessage,
            error
          ); /* eslint-disable-line no-console */
          context.error.migrationRead = errorMessage;
        }
      );
    },
    migrationReadSuccess(output) {
      this.apps = output.migration;
    },
    migrationUpdate(app, action) {
      const context = this;
      context.loading.migrationUpdate = true;

      app.status = "syncing";

      const migrationObj = {
        app: app.id,
        action: action,
      };

      nethserver.notifications.success = this.$i18n.t(
        "dashboard.synchronization_successful"
      );
      nethserver.notifications.error = this.$i18n.t(
        "dashboard.synchronization_failed"
      );

      nethserver.exec(
        ["nethserver-ns8-migration/migration/update"],
        migrationObj,
        function(stream) {
          console.info("ns8-migration-update", stream);
        },
        function(success) {
          context.loading.migrationUpdate = false;
          context.migrationRead();
        },
        function(error) {
          console.error(error);
          context.loading.migrationUpdate = false;
        }
      );
    },
    // showErrorMessage(errorMessage, error) { ////
    //   console.error(errorMessage, error); /* eslint-disable-line no-console */
    //   this.error.read = errorMessage;
    // },
    // closeErrorMessage() {
    //   this.error.read = null;
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
  margin-left: 8px;
}

.status-icon {
  margin-right: 7px;
  font-size: 16px;
  position: relative;
  top: 2px;
}
</style>