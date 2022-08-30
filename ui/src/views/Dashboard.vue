<template>
  <div>
    <h2>{{ $t("dashboard.title") }}</h2>
    <div v-if="error.listApplications" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.listApplications }}
    </div>
    <div v-if="error.connectionRead" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.connectionRead }}
    </div>
    <div
      v-if="loading.listApplications || loading.connectionRead"
      class="spinner spinner-lg"
    ></div>
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

        <div
          v-if="accountProviderMigrationStarted"
          class="alert alert-info alert-dismissable"
        >
          <span class="pficon pficon-info"></span>
          <strong
            >{{
              $t("dashboard.account_provider_migration_in_progress")
            }}:</strong
          >
          {{
            $t("dashboard.account_provider_migration_in_progress_description")
          }}
        </div>
        <div id="pf-list-default" class="list-group list-view-pf app-list">
          <div v-for="app in apps" :key="app.name" class="list-group-item">
            <div class="list-view-pf-actions migration-buttons">
              <button
                v-if="app.status == 'not_migrated'"
                @click="startMigration(app)"
                :disabled="loading.migrationUpdate"
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
              <template
                v-else-if="app.status == 'migrating' || app.status == 'syncing'"
              >
                <button
                  v-if="app.id != 'account-provider'"
                  @click="syncData(app)"
                  :disabled="loading.migrationUpdate || app.status == 'syncing'"
                  class="btn btn-primary"
                >
                  {{ $t("dashboard.sync_data") }}
                </button>
                <button
                  @click="finishMigration(app)"
                  :disabled="loading.migrationUpdate || app.status == 'syncing'"
                  class="btn btn-default"
                >
                  {{ $t("dashboard.finish_migration") }}
                </button>
              </template>
              <button
                v-else-if="app.status == 'migrated'"
                disabled
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
            </div>
            <div class="list-view-pf-main-info">
              <div class="list-view-pf-left">
                <!-- //// remove -->
                <img
                  v-if="app.id === 'account-provider'"
                  class="apps-icon"
                  src="logo.png"
                />
                <!--  //// remove v-else -->
                <img
                  v-else
                  class="apps-icon"
                  :src="'../' + app.id + '/' + (app.icon || 'logo.png')"
                />
              </div>
              <div class="list-view-pf-body">
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
      </template>
    </div>
    <!-- start migration modal -->
    <div
      class="modal"
      id="start-migration-modal"
      tabindex="-1"
      role="dialog"
      data-backdrop="static"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              {{ $t("dashboard.start_migration") }}
            </h4>
          </div>
          <form class="form-horizontal">
            <div class="modal-body">
              <template v-if="currentApp">
                <template v-if="currentApp.id === 'nethserver-nextcloud'">
                  <!-- choose a virtual host -->
                  <div class="mg-bottom-20">
                    {{ $t("dashboard.virtual_host_explanation") }}
                  </div>
                  <div
                    :class="['form-group', { 'has-error': error.virtualHost }]"
                  >
                    <label class="col-sm-3 control-label" for="virtual-host">
                      {{ $t("dashboard.virtual_host") }}
                    </label>
                    <div class="col-sm-7">
                      <input
                        v-model.trim="virtualHost"
                        id="virtual-host"
                        ref="virtualHost"
                        class="form-control"
                      />
                      <!--  //// validate virtual host -->
                      <span v-if="error.virtualHost" class="help-block">{{
                        error.virtualHost
                      }}</span>
                    </div>
                  </div>
                </template>
                <template v-if="currentApp.id === 'account-provider'">
                  <div class="mg-bottom-20">
                    {{
                      $t(
                        "dashboard.start_account_provider_migration_explanation"
                      )
                    }}
                  </div>
                </template>
              </template>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-default"
                @click="hideStartMigrationModal"
              >
                {{ $t("cancel") }}
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="startMigrationFromModal"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- finish migration modal -->
    <div
      class="modal"
      id="finish-migration-modal"
      tabindex="-1"
      role="dialog"
      data-backdrop="static"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              {{ $t("dashboard.finish_migration") }}
            </h4>
          </div>
          <form class="form-horizontal">
            <div class="modal-body">
              <template v-if="currentApp">
                <template v-if="currentApp.id === 'account-provider'">
                  <!-- choose an IP address for AD -->
                  <div class="mg-bottom-20">
                    {{ $t("dashboard.ad_ip_address_explanation") }}
                  </div>
                  <div
                    :class="['form-group', { 'has-error': error.adIpAddress }]"
                  >
                    <label class="col-sm-4 control-label" for="ad-ip-address">
                      {{ $t("dashboard.ad_ip_address") }}
                    </label>
                    <div class="col-sm-6">
                      <select
                        v-model="adIpAddress"
                        class="combobox form-control"
                        id="ad-ip-address"
                      >
                        <option
                          v-for="(ip, i) in adIpAddresses"
                          v-bind:key="i"
                          :value="ip"
                        >
                          {{ ip }}
                        </option>
                      </select>
                      <span v-if="error.adIpAddress" class="help-block">{{
                        error.adIpAddress
                      }}</span>
                    </div>
                  </div>
                </template>
              </template>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-default"
                @click="hideFinishMigrationModal"
              >
                {{ $t("cancel") }}
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="finishMigrationFromModal"
              >
                {{ $t("dashboard.finish_migration") }}
              </button>
            </div>
          </form>
        </div>
      </div>
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
      installedApps: [],
      apps: [],
      currentApp: null,
      virtualHost: "",
      isShownStartMigrationModal: false,
      isShownFinishMigrationModal: false,
      adIpAddress: "",
      adIpAddresses: ["1.1.1.1", "2.2.2.2"], //// get from api
      loading: {
        connectionRead: false,
        connectionUpdate: false,
        migrationRead: false,
        migrationUpdate: false,
        listApplications: false,
      },
      error: {
        connectionRead: "",
        connectionUpdate: "",
        migrationRead: "",
        migrationUpdate: "",
        leaderNode: "",
        adminUsername: "",
        adminPassword: "",
        listApplications: "",
        virtualHost: "",
        adIpAddress: "",
      },
    };
  },
  computed: {
    accountProviderApp() {
      return this.apps.find((app) => app.id === "account-provider");
    },
    accountProviderMigrationStarted() {
      if (this.accountProviderApp) {
        return this.accountProviderApp.status === "migrating";
      }
      return false;
    },
  },
  watch: {
    isShownStartMigrationModal: function() {
      if (this.isShownStartMigrationModal) {
        this.error.virtualHost = "";
        this.virtualHost = "";
        $("#start-migration-modal").modal("show");

        this.$nextTick(() => {
          if (this.$refs.virtualHost) {
            this.$refs.virtualHost.focus();
          }
        });
      } else {
        $("#start-migration-modal").modal("hide");
      }
    },
    isShownFinishMigrationModal: function() {
      if (this.isShownFinishMigrationModal) {
        this.error.adIpAddress = "";
        this.adIpAddress = "";
        $("#finish-migration-modal").modal("show");
      } else {
        $("#finish-migration-modal").modal("hide");
      }
    },
  },
  mounted() {
    this.listApplications();
  },
  methods: {
    togglePassword() {
      this.isPasswordVisible = !this.isPasswordVisible;
    },
    isStartMigrationModalNeeded(app) {
      return (
        (app.id === "nethserver-nextcloud" && !app.config.props.VirtualHost) ||
        app.id === "account-provider"
      );
    },
    isFinishMigrationModalNeeded(app) {
      return app.id === "account-provider" && app.provider === "ad";
    },
    startMigration(app) {
      if (this.isStartMigrationModalNeeded(app)) {
        this.currentApp = app;
        this.isShownStartMigrationModal = true;
      } else {
        this.migrationUpdate(app, "start");
      }
    },
    validateStartMigrationFromModal() {
      let isValidationOk = true;

      if (this.currentApp.id === "nethserver-nextcloud") {
        this.error.virtualHost = "";

        if (!this.virtualHost) {
          this.error.virtualHost = this.$t("validation.virtual_host_empty");
          this.$refs.virtualHost.focus();
          isValidationOk = false;
        }
      }
      return isValidationOk;
    },
    startMigrationFromModal() {
      const isValidationOk = this.validateStartMigrationFromModal();
      if (!isValidationOk) {
        return;
      }
      this.migrationUpdate(this.currentApp, "start");
      this.hideStartMigrationModal();
    },
    validateFinishMigrationFromModal() {
      let isValidationOk = true;

      if (this.currentApp.id === "account-provider") {
        this.error.adIpAddress = "";

        if (!this.adIpAddress) {
          this.error.adIpAddress = this.$t("validation.ad_ip_address_empty");
          isValidationOk = false;
        }
      }
      return isValidationOk;
    },
    finishMigrationFromModal() {
      const isValidationOk = this.validateFinishMigrationFromModal();
      if (!isValidationOk) {
        return;
      }
      this.migrationUpdate(this.currentApp, "finish");
      this.hideFinishMigrationModal();
    },
    finishMigration(app) {
      if (this.isFinishMigrationModalNeeded(app)) {
        this.currentApp = app;
        this.isShownFinishMigrationModal = true;
      } else {
        this.migrationUpdate(app, "finish");
      }
    },
    syncData(app) {
      this.migrationUpdate(app, "sync");
    },
    disconnectFromCluster() {
      this.config.isConnected = false; //// TODO
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
      const agentStatus = output.configuration.agent.props.status;
      this.config.isConnected = agentStatus == "enabled";
      const ns8Config = output.configuration.ns8.props;
      this.config.leaderNode =
        ns8Config.Host || "dn1.leader.cluster0.al.nethserver.net"; //// remove || ...
      this.config.adminUsername = ns8Config.User || "admin"; //// remove || ...
      this.config.adminPassword = ns8Config.Password || "Nethesis,1234"; //// remove || ...
      this.config.tlsVerify = ns8Config.TLSVerify == "enabled";
      this.loading.connectionRead = false;

      if (this.config.isConnected) {
        this.migrationRead();
      } else {
        this.$nextTick(() => {
          this.$refs.leaderNode.focus();
        });
      }
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
      this.apps = output.migration.filter(
        (app) =>
          this.installedApps.includes(app.id) ||
          (app.id === "account-provider" && app.provider != "none")
      );
    },
    migrationUpdate(app, action) {
      const context = this;
      context.loading.migrationUpdate = true;

      app.status = "syncing";

      //// remove mock
      // if (app.id === "account-provider") {
      //   setTimeout(() => {
      //     app.status = "migrating";
      //     context.accountProviderMigrationStarted = true;
      //     context.loading.migrationUpdate = false;
      //   }, 2000);
      //   return;
      // }
      //// end mock

      //// pass extra parameters if needed (virtualhost, ip address...)
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
    listApplications() {
      const context = this;
      context.loading.listApplications = true;
      nethserver.exec(
        ["system-apps/read"],
        {
          action: "list",
        },
        null,
        function(success) {
          const output = JSON.parse(success);
          context.listApplicationsSuccess(output);
        },
        function(error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_apps"
          );
          console.error(errorMessage, error);
          context.error.listApplications = errorMessage;
        },
        false
      );
    },
    listApplicationsSuccess(output) {
      this.installedApps = output.map((app) => app.id);
      this.loading.listApplications = false;
      this.connectionRead();
    },
    hideStartMigrationModal() {
      this.isShownStartMigrationModal = false;
    },
    hideFinishMigrationModal() {
      this.isShownFinishMigrationModal = false;
    },
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

.mg-bottom-20 {
  margin-bottom: 20px;
}

.migration-buttons {
  width: 33%;
  display: flex;
  justify-content: flex-end;
}
</style>
