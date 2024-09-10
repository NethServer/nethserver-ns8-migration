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
    <div v-if="error.connectionUpdate" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.connectionUpdate }}
      <pre v-if="error.rawConnectionUpdateMessage">{{ error.rawConnectionUpdateMessage }}</pre>
    </div>
    <div v-if="error.migrationRead" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.migrationRead }}
    </div>
    <div v-if="error.migrationUpdate" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.migrationUpdate }}
    </div>
    <div v-if="error.listPackagesToRemove" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.listPackagesToRemove }}
    </div>
    <div v-if="error.removePackages" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.removePackages }}
    </div>
    <div v-if="error.getAccountProviderInfo" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.getAccountProviderInfo }}
    </div>
    <div v-if="error.userDomains" class="alert alert-danger">
      <span class="pficon pficon-error-circle-o"></span>
      {{ error.userDomains }}
    </div>
    <div
      v-if="
        loading.listApplications ||
        loading.connectionRead ||
        loading.migrationRead ||
        loading.accountProviderInfo ||
        loading.abortAction
      "
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
                    !isPasswordVisible ? 'fa fa-eye' : 'fa fa-eye-slash'
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
          <span>{{
            $t("dashboard.connected_description", {
              leaderNode: config.leaderNode
            })
          }}</span>
          <span>
            <a class="disconnect-link" @click="showLogoutModal"
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
        <div
          id="pf-list-default"
          class="list-group list-view-pf app-list"
          v-if="validUserDomains"
        >
          <div v-for="app in apps" :key="app.id" class="list-group-item">
            <div class="list-view-pf-actions migration-buttons">
              <!-- local account provider -->
              <button
                v-if="
                  app.id == 'account-provider' &&
                  accountProviderConfig.location == 'local' &&
                  app.status == 'not_migrated'
                "
                @click="showStartMigrationModal(app)"
                :disabled="
                  loading.migrationUpdate || !canStartAccountProviderMigration
                "
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
              <!-- remote account provider -->
              <button
                v-else-if="
                  app.id == 'account-provider' &&
                  accountProviderConfig.location == 'remote' &&
                  app.status == 'not_migrated'
                "
                @click="showLogoutModalRemoteLdap()"
                :disabled="
                  loading.migrationUpdate || !canStartAccountProviderMigration
                "
                class="btn btn-default"
              >
                {{ $t("dashboard.finish_migration") }}
              </button>
              <!-- other apps -->
              <template
                v-else-if="
                  app.status == 'not_migrated' || app.status == 'skipped'
                "
              >
                <button
                  @click="showStartMigrationModal(app)"
                  :disabled="isStartMigrationButtonDisabled(app)"
                  v-if="!isMailChild(app) && !isAdChild(app)"
                  class="btn btn-default"
                >
                  {{ $t("dashboard.start_migration") }}
                </button>
                <button
                  @click="toggleSkip(app)"
                  :disabled="
                    loading.migrationUpdate || accountProviderMigrationStarted
                  "
                  v-if="!isMailChild(app)"
                  class="btn btn-default"
                >
                  {{
                    app.status == "skipped"
                      ? $t("dashboard.no_skip")
                      : $t("dashboard.skip")
                  }}
                </button>
              </template>
              <template
                v-else-if="app.status == 'migrating' || app.status == 'syncing'"
              >
                <button
                  @click="syncData(app)"
                  :disabled="loading.migrationUpdate || app.status == 'syncing'"
                  v-if="!isMailChild(app) && !isAdChild(app)"
                  class="btn btn-primary"
                >
                  {{ $t("dashboard.sync_data") }}
                </button>
                <button
                  @click="showFinishMigrationModal(app)"
                  :disabled="loading.migrationUpdate || app.status == 'syncing'"
                  v-if="!isMailChild(app) && !isAdChild(app)"
                  class="btn btn-default"
                >
                  {{ $t("dashboard.finish_migration") }}
                </button>
                <button
                  @click="showAbortModal(app)"
                  :disabled="loading.migrationUpdate || app.status == 'syncing'"
                  v-if="!isMailChild(app) && !isAdChild(app)"
                  class="btn btn-default"
                >
                  {{ $t("dashboard.abort") }}
                </button>
              </template>
              <button
                v-else-if="
                  app.status == 'migrated' &&
                  !isMailChild(app) &&
                  !isAdChild(app)
                "
                disabled
                class="btn btn-default"
              >
                {{ $t("dashboard.start_migration") }}
              </button>
            </div>
            <div class="list-view-pf-main-info">
              <div class="list-view-pf-left">
                <img
                  v-if="app.id === 'account-provider'"
                  class="apps-icon"
                  src="logo.png"
                />
                <img
                  v-else
                  :class="['apps-icon', { skipped: app.status == 'skipped' }]"
                  :src="'../' + app.id + '/' + (app.icon || 'logo.png')"
                  @error="$event.target.src = 'logo.png'"
                />
              </div>
              <div class="list-view-pf-body">
                <div class="list-group-item-heading">
                  <span>{{ app.name }}</span>
                </div>
                <!-- migration info -->
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
                  <span
                    v-else-if="app.status == 'skipped'"
                    class="fa fa-ban status-icon"
                  ></span>
                  <!-- email apps status description -->
                  <span
                    v-if="
                      [
                        'nethserver-sogo',
                        'nethserver-roundcubemail',
                        'nethserver-webtop5',
                        'nethserver-mail-getmail'
                      ].includes(app.id) && app.status != 'skipped'
                    "
                    >{{ $t("dashboard.app_migrated_with_email") }}
                  </span>
                  <!-- samba app status description -->
                  <span
                    v-else-if="
                      app.id === 'nethserver-samba' &&
                      app.status != 'skipped' &&
                      app.status != 'not_migratable'
                    "
                    >{{ $t("dashboard.app_migrated_with_ad") }}
                  </span>
                  <!-- remote account provider status description -->
                  <span
                    v-else-if="
                      app.id === 'account-provider' &&
                      accountProviderConfig.location === 'remote'
                    "
                  >
                    {{ $t("dashboard.remote_account_provider") }}
                  </span>
                  <!-- local account provider status description -->
                  <span
                    v-else-if="
                      app.id === 'account-provider' &&
                      accountProviderConfig.location === 'local' &&
                      !canStartAccountProviderMigration
                    "
                  >
                    {{ $t("dashboard.local_account_provider_migrate_last") }}
                  </span>
                  <!-- standard status description -->
                  <span v-else>{{ $t("dashboard.status_" + app.status) }}</span>
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
                <div v-if="error.getClusterStatus" class="alert alert-danger">
                  <span class="pficon pficon-error-circle-o"></span>
                  {{ error.getClusterStatus }}
                </div>
                <template v-if="currentApp.id === 'account-provider'">
                  <div class="mg-bottom-20">
                    {{
                      $t(
                        "dashboard.start_account_provider_migration_explanation",
                        { leaderNode: config.leaderNode }
                      )
                    }}
                  </div>
                </template>
                <template v-else>
                  <div class="mg-bottom-20">
                    <div>
                      {{
                        $t("dashboard.app_will_be_migrated", {
                          appName: currentApp.name,
                          leaderNode: config.leaderNode
                        })
                      }}
                    </div>
                    <div
                      class="mg-top-10"
                      v-if="currentApp.id === 'nethserver-mail' && !sogoApp"
                    >
                      {{ $t("dashboard.roundcube_webtop_migration") }}
                    </div>
                    <div
                      class="mg-top-10"
                      v-if="currentApp.id === 'nethserver-mail' && sogoApp"
                    >
                      {{ $t("dashboard.roundcube_webtop_sogo_migration") }}
                    </div>
                    <div class="mg-top-10" v-if="sogoApp">
                      {{ $t("dashboard.enable_forge_sogo") }}
                    </div>
                  </div>
                </template>
                <!-- loading nodes -->
                <div v-if="loading.getClusterStatus">
                  <span class="control-label">
                    {{ $t("dashboard.loading_nodes") }}
                  </span>
                  <div
                    class="spinner spinner-sm form-spinner-loader adjust-top-loader node-spinner"
                  ></div>
                </div>
                <!-- node selection -->
                <template v-if="clusterNodes.length > 1">
                  <template v-if="currentApp.id === 'nethserver-mail'">
                    <!-- node selection for email apps -->
                    <div class="form-group">
                      <label class="col-sm-5 control-label" for="email-node">
                        {{ $t("dashboard.destination_node_for_email") }}
                      </label>
                      <div class="col-sm-6">
                        <select
                          v-model="emailNode"
                          class="combobox form-control"
                          id="email-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div v-if="roundcubeApp" class="form-group">
                      <label
                        class="col-sm-5 control-label"
                        for="roundcube-node"
                      >
                        {{ $t("dashboard.destination_node_for_roundcube") }}
                      </label>
                      <div class="col-sm-6">
                        <select
                          v-model="roundcubeNode"
                          class="combobox form-control"
                          id="roundcube-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div v-if="nethvoiceApp" class="form-group">
                      <label
                        class="col-sm-5 control-label"
                        for="nethvoice-node"
                      >
                        {{ $t("dashboard.destination_node_for_nethvoice") }}
                      </label>
                      <div class="col-sm-6">
                        <select
                          v-model="nethvoiceNode"
                          class="combobox form-control"
                          id="nethvoice-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div v-if="sogoApp" class="form-group">
                      <label class="col-sm-5 control-label" for="sogo-node">
                        {{ $t("dashboard.destination_node_for_sogo") }}
                      </label>
                      <div class="col-sm-6">
                        <select
                          v-model="sogoNode"
                          class="combobox form-control"
                          id="sogo-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div v-if="webtopApp" class="form-group">
                      <label class="col-sm-5 control-label" for="webtop-node">
                        {{ $t("dashboard.destination_node_for_webtop") }}
                      </label>
                      <div class="col-sm-6">
                        <select
                          v-model="webtopNode"
                          class="combobox form-control"
                          id="webtop-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div v-if="getmailApp" class="form-group">
                      <label class="col-sm-5 control-label" for="getmail-node">
                        {{ $t("dashboard.destination_node_for_getmail") }}
                      </label>
                      <div class="col-sm-6">
                        <select
                          v-model="getmailNode"
                          class="combobox form-control"
                          id="getmail-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <!-- node selection for app-->
                    <div class="form-group">
                      <label class="col-sm-5 control-label" for="app-node">
                        {{
                          $t("dashboard.destination_node", {
                            app: currentApp.name
                          })
                        }}
                      </label>
                      <div
                        v-if="loading.getClusterStatus"
                        class="spinner spinner-sm form-spinner-loader adjust-top-loader node-spinner"
                      ></div>
                      <div v-else class="col-sm-6">
                        <select
                          v-model="appNode"
                          class="combobox form-control"
                          id="app-node"
                        >
                          <option
                            v-for="node in clusterNodes"
                            v-bind:key="node.id"
                            :value="node.id"
                            :disabled="!node.online"
                          >
                            {{ getNodeLabel(node) }}
                          </option>
                        </select>
                      </div>
                    </div>
                  </template>
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
                :disabled="loading.getClusterStatus || !!error.getClusterStatus"
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
                  <template v-if="currentApp.provider === 'ad'">
                    <!-- choose an IP address for AD -->
                    <div class="mg-bottom-20">
                      {{ $t("dashboard.ad_ip_address_explanation") }}
                    </div>
                    <div
                      :class="[
                        'form-group',
                        'mg-bottom-20',
                        { 'has-error': error.adIpAddress }
                      ]"
                    >
                      <label class="col-sm-5 control-label" for="ad-ip-address">
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
                            :value="ip.ipaddress"
                          >
                            {{ ip.ipaddress }} - {{ ip.label }}
                          </option>
                        </select>
                        <span v-if="error.adIpAddress" class="help-block">{{
                          error.adIpAddress
                        }}</span>
                      </div>
                    </div>
                    <div class="mg-bottom-20">
                      {{
                        $t(
                          "dashboard.finish_account_provider_migration_explanation"
                        )
                      }}
                    </div>
                  </template>
                  <template v-else>
                    <!-- LDAP -->
                    <div class="mg-bottom-20">
                      {{
                        $t(
                          "dashboard.finish_account_provider_migration_explanation"
                        )
                      }}
                    </div>
                  </template>
                </template>
                <template v-else>
                  <div class="mg-bottom-20">
                    {{
                      $t("dashboard.finish_app_migration_explanation", {
                        appName: currentApp.name
                      })
                    }}
                  </div>
                  <template
                    v-if="
                      currentApp.id === 'nethserver-nextcloud' &&
                      !nextcloudApp.config.props.VirtualHost
                    "
                  >
                    <!-- choose a virtual host for Nextcloud -->
                    <div class="mg-bottom-20">
                      <span
                        >{{ $t("dashboard.virtual_host_explanation") }}
                      </span>
                    </div>
                    <div
                      :class="[
                        'form-group',
                        { 'has-error': error.virtualHost }
                      ]"
                    >
                      <label class="col-sm-5 control-label" for="virtual-host">
                        {{ $t("dashboard.nextcloud_virtual_host") }}
                      </label>
                      <div class="col-sm-6">
                        <input
                          v-model.trim="virtualHost"
                          id="virtual-host"
                          ref="virtualHost"
                          class="form-control"
                        />
                        <span v-if="error.virtualHost" class="help-block">{{
                          error.virtualHost
                        }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-if="currentApp.id === 'nethserver-mail'">
                    <!-- virtual host for roundcube -->
                    <div
                      v-if="roundcubeApp"
                      :class="[
                        'form-group',
                        { 'has-error': error.roundCubeVirtualHost }
                      ]"
                    >
                      <label
                        class="col-sm-5 control-label"
                        for="roundcube-virtual-host"
                      >
                        {{ $t("dashboard.roundcube_virtual_host") }}
                      </label>
                      <div class="col-sm-6">
                        <input
                          v-model.trim="roundCubeVirtualHost"
                          id="roundcube-virtual-host"
                          ref="roundcubeVirtualHost"
                          class="form-control"
                        />
                        <span
                          v-if="error.roundCubeVirtualHost"
                          class="help-block"
                          >{{ error.roundCubeVirtualHost }}</span
                        >
                      </div>
                    </div>
                    <!-- virtual host for sogo -->
                    <div
                      v-if="sogoApp"
                      :class="[
                        'form-group',
                        { 'has-error': error.sogoVirtualHost }
                      ]"
                    >
                      <label
                        class="col-sm-5 control-label"
                        for="sogo-virtual-host"
                      >
                        {{ $t("dashboard.sogo_virtual_host") }}
                      </label>
                      <div class="col-sm-6">
                        <input
                          v-model.trim="sogoVirtualHost"
                          id="sogo-virtual-host"
                          ref="sogoVirtualHost"
                          class="form-control"
                        />
                        <span v-if="error.sogoVirtualHost" class="help-block">{{
                          error.sogoVirtualHost
                        }}</span>
                      </div>
                    </div>
                    <!-- virtual host for webtop -->
                    <div
                      v-if="webtopApp && !webtopApp.config.props.VirtualHost"
                      :class="[
                        'form-group',
                        { 'has-error': error.webtopVirtualHost }
                      ]"
                    >
                      <label
                        class="col-sm-5 control-label"
                        for="webtop-virtual-host"
                      >
                        {{ $t("dashboard.webtop_virtual_host") }}
                      </label>
                      <div class="col-sm-6">
                        <input
                          v-model.trim="webtopVirtualHost"
                          id="webtop-virtual-host"
                          ref="webtopVirtualHost"
                          class="form-control"
                        />
                        <span
                          v-if="error.webtopVirtualHost"
                          class="help-block"
                          >{{ error.webtopVirtualHost }}</span
                        >
                      </div>
                    </div>
                  </template>
                  <template v-if="currentApp.id === 'nethserver-nethvoice14'">
                    <!-- virtual host for nethvoice and CTI -->
                    <div
                      :class="[
                        'form-group',
                        { 'has-error': error.nethVoiceVirtualHost }
                      ]"
                    >
                      <label
                        class="col-sm-5 control-label"
                        for="nethvoice-virtual-host"
                      >
                        {{ $t("dashboard.nethvoice_virtual_host") }}
                      </label>
                      <div class="col-sm-6">
                        <input
                          v-model.trim="nethVoiceVirtualHost"
                          id="nethvoice-virtual-host"
                          ref="nethVoiceVirtualHost"
                          class="form-control"
                        />
                        <span
                          v-if="error.nethVoiceVirtualHost"
                          class="help-block"
                          >{{ error.nethVoiceVirtualHost }}</span
                        >
                      </div>
                    </div>
                    <div
                      :class="[
                        'form-group',
                        { 'has-error': error.ctiVirtualHost }
                      ]"
                    >
                      <label
                        class="col-sm-5 control-label"
                        for="cti-virtual-host"
                      >
                        {{ $t("dashboard.cti_virtual_host") }}
                      </label>
                      <div class="col-sm-6">
                        <input
                          v-model.trim="ctiVirtualHost"
                          id="cti-virtual-host"
                          ref="ctiVirtualHost"
                          class="form-control"
                        />
                        <span v-if="error.ctiVirtualHost" class="help-block">{{
                          error.ctiVirtualHost
                        }}</span>
                      </div>
                    </div>
                  </template>
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
    <!-- abort modal -->
    <div
      class="modal"
      id="abort-modal"
      tabindex="-1"
      role="dialog"
      data-backdrop="static"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              {{ $t("dashboard.abort") }}: {{ abortApp ? abortApp.name : "" }}
            </h4>
          </div>
          <form class="form-horizontal">
            <div class="modal-body">
              <div>
                {{
                  $t("dashboard.abort_current_app", {
                    app: abortApp ? abortApp.name : ""
                  })
                }}
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-default"
                @click="hideAbortModal"
              >
                {{ $t("cancel") }}
              </button>
              <button
                type="button"
                class="btn btn-danger"
                @click="abort(abortApp)"
              >
                {{ $t("dashboard.abort") }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- logout modal -->
    <div
      class="modal"
      id="logout-modal"
      tabindex="-1"
      role="dialog"
      data-backdrop="static"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h4 class="modal-title">
              {{ $t("dashboard.disconnect_from_ns8_cluster") }}
            </h4>
          </div>
          <form class="form-horizontal">
            <div class="modal-body">
              <!-- logout not allowed -->
              <div v-if="someAppsHaveFinishedMigration">
                {{ $t("dashboard.disconnect_not_allowed_explanation") }}
              </div>
              <!-- logout allowed -->
              <div v-else>
                {{
                  $t("dashboard.disconnect_explanation", {
                    leaderNode: config.leaderNode
                  })
                }}
              </div>
            </div>
            <div class="modal-footer">
              <template v-if="someAppsHaveFinishedMigration">
                <button
                  type="button"
                  class="btn btn-primary"
                  @click="hideLogoutModal"
                >
                  {{ $t("cancel") }}
                </button>
              </template>
              <template v-else>
                <button
                  type="button"
                  class="btn btn-default"
                  @click="hideLogoutModal"
                >
                  {{ $t("cancel") }}
                </button>
                <button
                  type="button"
                  class="btn btn-primary"
                  @click="connectionLogout"
                >
                  {{ $t("dashboard.disconnect") }}
                </button>
              </template>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- logout modal remote-account-provider -->
    <div
      class="modal"
      id="logout-modal-remote-account-provider"
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
              <!-- logout allowed -->
              <div>
                {{
                  $t(
                    "dashboard.disconnect_explanation_remote_account_provider",
                    {
                      leaderNode: config.leaderNode
                    }
                  )
                }}
              </div>
            </div>
            <div class="modal-footer">
              <template>
                <button
                  type="button"
                  class="btn btn-default"
                  @click="hideLogoutModal"
                >
                  {{ $t("cancel") }}
                </button>
                <button
                  type="button"
                  class="btn btn-primary"
                  @click="connectionLogout"
                >
                  {{ $t("dashboard.disconnect") }}
                </button>
              </template>
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
        adminPassword: ""
      },
      installedApps: [],
      apps: [],
      currentApp: null,
      abortApp: null,
      virtualHost: "",
      roundCubeVirtualHost: "",
      nethVoiceVirtualHost: "",
      ctiVirtualHost: "",
      sogoVirtualHost: "",
      webtopVirtualHost: "",
      adIpAddress: "",
      adIpAddresses: [],
      accountProviderConfig: null,
      appNode: 1,
      clusterNodes: [],
      emailNode: 1,
      webtopNode: 1,
      roundcubeNode: 1,
      sogoNode: 1,
      getmailNode: 1,
      validUserDomains: true,
      localDomain: "",
      allAppsMigrated: false,
      loading: {
        connectionRead: false,
        connectionUpdate: false,
        migrationRead: false,
        migrationUpdate: false,
        listApplications: false,
        accountProviderInfo: false,
        getClusterStatus: false,
        abortAction: false
      },
      error: {
        connectionRead: "",
        connectionUpdate: "",
        rawConnectionUpdateMessage: "",
        migrationRead: "",
        migrationUpdate: "",
        leaderNode: "",
        adminUsername: "",
        adminPassword: "",
        listApplications: "",
        accountProviderInfo: "",
        virtualHost: "",
        adIpAddress: "",
        listPackagesToRemove: "",
        removePackages: "",
        getClusterStatus: "",
        roundCubeVirtualHost: "",
        nethVoiceVirtualHost: "",
        ctiVirtualHost: "",
        sogoVirtualHost: "",
        webtopVirtualHost: "",
        userDomains: ""
      }
    };
  },
  computed: {
    accountProviderApp() {
      return this.apps.find((app) => app.id === "account-provider");
    },
    nextcloudApp() {
      return this.apps.find((app) => app.id === "nethserver-nextcloud");
    },
    accountProviderMigrationStarted() {
      if (this.accountProviderApp) {
        return this.accountProviderApp.status === "migrating";
      }
      return false;
    },
    someAppsHaveFinishedMigration() {
      return this.apps.some((app) => app.status === "migrated");
    },
    emailApp() {
      return this.apps.find((app) => app.id === "nethserver-mail");
    },
    roundcubeApp() {
      return this.apps.find((app) => app.id === "nethserver-roundcubemail");
    },
    nethvoiceApp() {
      return this.apps.find((app) => app.id === "nethserver-nethvoice14");
    },
    sogoApp() {
      return this.apps.find((app) => app.id === "nethserver-sogo");
    },
    webtopApp() {
      return this.apps.find((app) => app.id === "nethserver-webtop5");
    },
    getmailApp() {
      return this.apps.find((app) => app.id === "nethserver-mail-getmail");
    },
    canStartAccountProviderMigration() {
      // account provider migration can start only if it's local and all other apps have completed migration or have been skipped
      return !this.apps.some(
        (app) =>
          app.status !== "migrated" &&
          app.status !== "skipped" &&
          ![
            "account-provider",
            "nethserver-roundcubemail",
            "nethserver-nethvoice14",
            "nethserver-sogo",
            "nethserver-webtop5",
            "nethserver-mail-getmail",
            "nethserver-samba"
          ].includes(app.id)
      );
    }
  },
  mounted() {
    this.connectionRead();
  },
  methods: {
    togglePassword() {
      this.isPasswordVisible = !this.isPasswordVisible;
    },
    showAbortModal(app) {
      this.abortApp = app;
      $("#abort-modal").modal("show");
    },
    hideAbortModal() {
      $("#abort-modal").modal("hide");
    },
    showLogoutModal() {
      $("#logout-modal").modal("show");
    },
    hideLogoutModal() {
      $("#logout-modal").modal("hide");
      $("#logout-modal-remote-account-provider").modal("hide");
    },
    showLogoutModalRemoteLdap() {
      $("#logout-modal-remote-account-provider").modal("show");
    },
    showStartMigrationModal(app) {
      this.currentApp = app;
      $("#start-migration-modal").modal("show");

      // get cluster nodes
      this.migrationReadClusterStatus();
    },
    hideStartMigrationModal() {
      $("#start-migration-modal").modal("hide");
    },
    showFinishMigrationModal(app) {
      this.currentApp = app;
      this.error.virtualHost = "";
      this.error.adIpAddress = "";
      this.virtualHost = "";
      this.adIpAddress = "";
      this.roundCubeVirtualHost = "";
      (this.nethVoiceVirtualHost = ""),
        (this.ctiVirtualHost = ""),
        (this.webtopVirtualHost = "");
      this.error.roundCubeVirtualHost = "";
      this.error.nethVoiceVirtualHost = "";
      this.error.ctiVirtualHost = "";
      this.sogoVirtualHost = "";
      this.webtopVirtualHost = "";
      this.error.roundCubeVirtualHost = "";
      this.error.sogoVirtualHost = "";
      this.error.webtopVirtualHost = "";
      $("#finish-migration-modal").modal("show");

      this.$nextTick(() => {
        if (this.$refs.virtualHost) {
          this.$refs.virtualHost.focus();
        } else if (this.$refs.roundcubeVirtualHost) {
          this.$refs.roundcubeVirtualHost.focus();
        } else if (this.$refs.nethVoiceVirtualHost) {
          this.$refs.nethVoiceVirtualHost.focus();
        } else if (this.$refs.ctiVirtualHost) {
          this.$refs.ctiVirtualHost.focus();
        }
      });
    },
    hideFinishMigrationModal() {
      $("#finish-migration-modal").modal("hide");
    },
    validateStartMigrationFromModal() {
      let isValidationOk = true;
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
    cleanValidationError() {
      // clean error messages for validation
      this.error.virtualHost = "";
      this.error.adIpAddress = "";
      this.error.roundCubeVirtualHost = "";
      this.error.nethVoiceVirtualHost = "";
      this.error.ctiVirtualHost = "";
      this.error.sogoVirtualHost = "";
      this.error.webtopVirtualHost = "";
      this.error.userDomains = "";
    },
    validateFinishMigrationFromModal() {
      let isValidationOk = true;

      this.cleanValidationError();

      if (this.currentApp.id === "nethserver-nextcloud") {
        // nextcloud

        this.error.virtualHost = "";

        if (!this.nextcloudApp.config.props.VirtualHost && !this.virtualHost) {
          this.error.virtualHost = this.$t("validation.virtual_host_empty");
          this.$refs.virtualHost.focus();
          isValidationOk = false;
        }
      } else if (this.currentApp.id === "nethserver-nethvoice14") {
        // nethvoice

        if (this.nethvoiceApp && !this.nethVoiceVirtualHost) {
          this.error.nethVoiceVirtualHost = this.$t(
            "validation.virtual_host_empty"
          );

          if (isValidationOk) {
            this.$refs.nethVoiceVirtualHost.focus();
            isValidationOk = false;
          }
        }

        if (this.nethvoiceApp && !this.ctiVirtualHost) {
          this.error.ctiVirtualHost = this.$t("validation.virtual_host_empty");

          if (isValidationOk) {
            this.$refs.ctiVirtualHost.focus();
            isValidationOk = false;
          }
        }

        if (
          this.ctiVirtualHost &&
          this.ctiVirtualHost === this.nethVoiceVirtualHost
        ) {
          this.error.ctiVirtualHost = this.$t(
            "validation.virtualhost_cannot_be_the_same"
          );

          if (isValidationOk) {
            this.$refs.ctiVirtualHost.focus();
            isValidationOk = false;
          }
        }
      } else if (this.currentApp.id === "account-provider") {
        // account provider

        this.error.adIpAddress = "";

        if (this.currentApp.provider === "ad" && !this.adIpAddress) {
          this.error.adIpAddress = this.$t("validation.ad_ip_address_empty");
          isValidationOk = false;
        }
      } else if (this.currentApp.id === "nethserver-mail") {
        // email

        this.error.roundCubeVirtualHost = "";
        this.error.nethVoiceVirtualHost = "";
        this.error.ctiVirtualHost = "";
        this.error.sogoVirtualHost = "";
        this.error.webtopVirtualHost = "";

        if (this.roundcubeApp && !this.roundCubeVirtualHost) {
          this.error.roundCubeVirtualHost = this.$t(
            "validation.virtual_host_empty"
          );

          if (isValidationOk) {
            this.$refs.roundcubeVirtualHost.focus();
            isValidationOk = false;
          }
        }

        if (this.sogoApp && !this.sogoVirtualHost) {
          this.error.sogoVirtualHost = this.$t("validation.virtual_host_empty");

          if (isValidationOk) {
            this.$refs.sogoVirtualHost.focus();
            isValidationOk = false;
          }
        }

        if (
          this.webtopApp &&
          !this.webtopApp.config.props.VirtualHost &&
          !this.webtopVirtualHost
        ) {
          this.error.webtopVirtualHost = this.$t(
            "validation.virtual_host_empty"
          );

          if (isValidationOk) {
            this.$refs.webtopVirtualHost.focus();
            isValidationOk = false;
          }
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
    syncData(app) {
      this.migrationUpdate(app, "sync");
    },
    connectionLogout() {
      this.loading.connectionUpdate = true;
      this.error.connectionUpdate = "";
      this.error.rawConnectionUpdateMessage = "";

      nethserver.notifications.success = this.$i18n.t(
        "dashboard.disconnect_successful"
      );
      nethserver.notifications.error = this.$i18n.t(
        "dashboard.disconnect_failed"
      );
      const context = this;
      nethserver.exec(
        ["nethserver-ns8-migration/connection/update"],
        { action: "logout" },
        function (stream) {
          console.info("ns8-migration-update", stream);
        },
        function (success) {
          context.loading.connectionUpdate = false;
          context.connectionRead();
        },
        function (error) {
          const errorMessage = context.$i18n.t("dashboard.error_logging_out");
          console.error(errorMessage, error);
          context.error.connectionUpdate = errorMessage;
          context.loading.connectionUpdate = false;
        }
      );
      this.hideLogoutModal();
    },
    connectionRead() {
      const context = this;
      context.loading.connectionRead = true;
      nethserver.exec(
        ["nethserver-ns8-migration/connection/read"],
        {},
        null,
        function (success) {
          const output = JSON.parse(success);
          context.connectionReadSuccess(output);
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_connection_data"
          );
          console.error(errorMessage, error);
          context.error.connectionRead = errorMessage;
          context.loading.connectionRead = false;
        }
      );
    },
    connectionReadSuccess(output) {
      const ns8Config = output.configuration.ns8.props;
      this.config.isConnected = ns8Config.Host != "";
      this.config.leaderNode = ns8Config.Host;
      this.config.adminUsername = ns8Config.User;
      this.config.adminPassword = ns8Config.Password;
      this.config.tlsVerify = ns8Config.TLSVerify == "enabled";
      this.loading.connectionRead = false;

      if (this.config.isConnected) {
        this.getAccountProviderInfo();
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
      this.error.connectionUpdate = "";
      this.error.rawConnectionUpdateMessage = "";

      var validateObj = {
        action: "login",
        Host: this.config.leaderNode,
        User: this.config.adminUsername,
        Password: this.config.adminPassword,
        TLSVerify: this.config.tlsVerify ? "enabled" : "disabled"
      };

      const context = this;
      nethserver.exec(
        ["nethserver-ns8-migration/connection/validate"],
        validateObj,
        null,
        function (success) {
          try {
            success = JSON.parse(success);
          } catch (e) {
            console.error(e);
          }
          context.connectionValidateSuccess(validateObj);
        },
        function (error, data) {
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
      var streamMessage = "";
      nethserver.exec(
        ["nethserver-ns8-migration/connection/update"],
        validateObj,
        function (message) {
          streamMessage = message;
        },
        function (success) {
          context.loading.connectionUpdate = false;
          context.connectionRead();
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_connecting_to_ns8"
          );
          console.error(errorMessage, error);
          context.error.connectionUpdate = errorMessage;
          context.error.rawConnectionUpdateMessage = streamMessage;
          context.loading.connectionUpdate = false;
        }
      );
    },
    migrationReadApps() {
      const context = this;
      context.loading.migrationRead = true;
      nethserver.exec(
        ["nethserver-ns8-migration/migration/read"],
        { action: "listApps" },
        null,
        function (success) {
          const output = JSON.parse(success);
          context.migrationReadAppsSuccess(output);
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_apps_to_migrate"
          );
          console.error(errorMessage, error);
          context.error.migrationRead = errorMessage;
          context.loading.migrationRead = false;
        }
      );
    },
    migrationReadAppsSuccess(output) {
      let apps = output.migration.filter(
        (app) =>
          this.installedApps.includes(app.id) ||
          (app.id === "account-provider" &&
            this.accountProviderConfig.type !== "none") ||
          app.status !== "not_migrated"
      );

      const accountProviderApp = apps.find(
        (app) => app.id === "account-provider"
      );

      if (accountProviderApp) {
        const type = this.accountProviderConfig.type;
        const location = this.accountProviderConfig.location;
        accountProviderApp.name = this.$t(`dashboard.${location}_${type}`);
      }

      apps.forEach((app) => {
        if (app.id === "account-provider" && app.provider === "ad") {
          this.adIpAddresses = app.ip_addresses;
        }
      });

      this.apps = apps;
      this.validUserDomains = output.validDomains;
      if (!this.validUserDomains) {
        if (this.accountProviderConfig.location === "remote") {
          this.error.userDomains = this.$t(
            "dashboard.external_user_domain_error"
          );
        } else {
          this.error.userDomains = this.$t(
            "dashboard.internal_user_domain_error",
            { domain: this.localDomain }
          );
        }
      }
      this.loading.migrationRead = false;
    },
    migrationUpdate(app, action) {
      const context = this;
      context.loading.migrationUpdate = true;
      const oldAppStatus = app.status;
      app.status = "syncing";

      const migrationObj = {
        app: app.id,
        action: action
      };

      if (action === "start") {
        if (app.id === "nethserver-mail") {
          let migrationConfig = {
            emailNode: this.emailNode
          };

          if (this.webtopApp) {
            migrationConfig.webtopNode = this.webtopNode;
          }

          if (this.getmailApp) {
            migrationConfig.getmailNode = this.getmailNode;
          }

          if (this.roundcubeApp) {
            migrationConfig.roundcubeNode = this.roundcubeNode;
          }

          if (this.sogoApp) {
            migrationConfig.sogoNode = this.sogoNode;
          }

          migrationObj.migrationConfig = migrationConfig;
        } else {
          migrationObj.migrationConfig = {
            appNode: this.appNode
          };
        }
      } else if (action === "finish") {
        // set migration configurations if needed

        if (app.id === "nethserver-nextcloud") {
          // if nextcloud virtualhost is already set, just uset it
          if (!this.virtualHost && this.nextcloudApp.config.props.VirtualHost) {
            this.virtualHost = this.nextcloudApp.config.props.VirtualHost;
          }
          migrationObj.migrationConfig = {
            virtualHost: this.virtualHost
          };
        } else if (app.id === "nethserver-nethvoice14") {
          let migrationConfig = {
            nethVoiceVirtualHost: this.nethVoiceVirtualHost,
            ctiVirtualHost: this.ctiVirtualHost
          };
          migrationObj.migrationConfig = migrationConfig;
        } else if (app.id === "nethserver-mail") {
          let migrationConfig = {
            roundCubeVirtualHost: this.roundCubeVirtualHost
          };
          // if webtop virtualhost is already set, just uset it
          if (this.webtopApp && this.webtopApp.config.props.VirtualHost) {
            migrationConfig.webtopVirtualHost =
              this.webtopApp.config.props.VirtualHost;
          } else if (this.webtopVirtualHost) {
            migrationConfig.webtopVirtualHost = this.webtopVirtualHost;
          }

          if (this.sogoVirtualHost) {
            migrationConfig.sogoVirtualHost = this.sogoVirtualHost;
          }

          migrationObj.migrationConfig = migrationConfig;
        } else if (app.id === "account-provider" && app.provider === "ad") {
          migrationObj.migrationConfig = { sambaIpAddress: this.adIpAddress };
        }
      }

      nethserver.notifications.success = this.$i18n.t(
        "dashboard.synchronization_successful"
      );
      nethserver.notifications.error = this.$i18n.t(
        "dashboard.synchronization_failed"
      );

      nethserver.exec(
        ["nethserver-ns8-migration/migration/update"],
        migrationObj,
        function (stream) {
          console.info("ns8-migration-update", stream);
        },
        function (success) {
          context.loading.migrationUpdate = false;
          console.log("test allAppsMigrated", context.allAppsMigrated);
          if (app.id === "account-provider" && app.installed === true) {
            // account provider is migrated last, api has already performed logout from ns8
            context.connectionRead();
          } else if ( context.allAppsMigrated ) {
            // log out everything is migrated <e have no account-provider app installed
            context.connectionLogout();
          } else {
            // reload migration status
            context.migrationReadApps();
          }
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_migrating_data"
          );
          console.error(errorMessage, error);
          context.error.migrationUpdate = errorMessage;
          context.loading.migrationUpdate = false;
          app.status = oldAppStatus;
        }
      );
    },
  checkMigrationStatus() {
    const context = this;
    // Call the migrationReadApps method and assign its return value to migrationData
    const migrationData = context.migrationReadApps();
    // Check if every app except account-provider is migrated
    const allMigratedExceptAccountProvider = migrationData.migration.every(app => app.id === "account-provider" || app.status === "migrated");
    // Check if the account-provider app is not installed
    const accountProviderNotInstalled = migrationData.migration.some(app => app.id === "account-provider" && !app.installed);
    // Return true if all apps except account-provider are migrated and the account-provider app is not installed
    return allMigratedExceptAccountProvider && accountProviderNotInstalled;
  },
    listApplications() {
      const context = this;
      context.loading.listApplications = true;
      nethserver.exec(
        ["system-apps/read"],
        {
          action: "list"
        },
        null,
        function (success) {
          const output = JSON.parse(success);
          context.listApplicationsSuccess(output);
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_apps"
          );
          console.error(errorMessage, error);
          context.error.listApplications = errorMessage;
          context.loading.listApplications = false;
        },
        false
      );
    },
    listApplicationsSuccess(output) {
      this.installedApps = output.map((app) => app.id);
      // some rpms are listed inside provides:[nethserver-mail-getmail, .. , ..]
      output.forEach((app) => {
        app.provides.forEach((item) => {
          this.installedApps.push(item);
        });
      });
      this.loading.listApplications = false;
      this.migrationReadApps();
    },
    abort(app) {
      const context = this;
      context.loading.migrationUpdate = true;
      context.loading.abortAction = true;
      context.hideAbortModal();
      nethserver.exec(
        ["nethserver-ns8-migration/migration/update"],
        {
          action: "abort",
          app: app.id
        },
        null,
        function (success) {
          context.migrationReadApps();
          context.loading.migrationUpdate = false;
          context.loading.abortAction = false;
        },
        function (error) {
          const errorMessage = context.$i18n.t("dashboard.error_on_abort");
          console.error(errorMessage, error);
          context.error.migrationUpdate = errorMessage;
          context.loading.migrationUpdate = false;
          context.loading.abortAction = false;
          context.migrationReadApps();
        },
        false
      );
    },
    toggleSkip(app) {
      const context = this;
      context.loading.migrationUpdate = true;
      nethserver.exec(
        ["nethserver-ns8-migration/migration/update"],
        {
          action: "toggle-skip",
          app: app.id
        },
        null,
        function (success) {
          context.migrationReadApps();
          context.loading.migrationUpdate = false;
        },
        function (error) {
          const errorMessage = context.$i18n.t("dashboard.error_on_skip");
          console.error(errorMessage, error);
          context.error.migrationUpdate = errorMessage;
          context.loading.migrationUpdate = false;
          context.migrationReadApps();
        }
      );
    },
    getAccountProviderInfo() {
      this.loading.accountProviderInfo = true;
      let context = this;
      nethserver.exec(
        ["system-accounts-provider/read"],
        {
          action: "dump"
        },
        null,
        function (success) {
          success = JSON.parse(success);
          const accountProviderConfig = success;

          // provider type

          if (accountProviderConfig.isLdap) {
            accountProviderConfig.type = "ldap";
          } else if (accountProviderConfig.isAD) {
            accountProviderConfig.type = "ad";
          } else {
            accountProviderConfig.type = "none";
          }

          context.localDomain = accountProviderConfig.BaseDN
            ? accountProviderConfig.BaseDN.substring(3).replaceAll(",dc=", ".")
            : "";
          // provider location

          const location = accountProviderConfig.IsLocal ? "local" : "remote";
          accountProviderConfig.location = location;
          context.accountProviderConfig = accountProviderConfig;
          context.loading.accountProviderInfo = false;
          context.listApplications();
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_account_provider_info"
          );
          console.error(errorMessage, error);
          context.error.getAccountProviderInfo = errorMessage;
          context.loading.getAccountProviderInfo = false;
        }
      );
    },
    migrationReadClusterStatus() {
      const context = this;
      context.clusterNodes = [];
      context.loading.getClusterStatus = true;
      context.error.getClusterStatus = "";

      nethserver.exec(
        ["nethserver-ns8-migration/migration/read"],
        { action: "getClusterStatus" },
        null,
        function (success) {
          const output = JSON.parse(success);
          context.migrationReadClusterStatusSuccess(output);
        },
        function (error) {
          const errorMessage = context.$i18n.t(
            "dashboard.error_retrieving_cluster_status"
          );
          console.error(errorMessage, error);
          context.error.getClusterStatus = errorMessage;
          context.loading.getClusterStatus = false;
        }
      );
    },
    migrationReadClusterStatusSuccess(output) {
      // check for ns8 action error
      if (output.clusterStatus.data.exit_code !== 0) {
        const errorMessage = this.$i18n.t(
          "dashboard.error_retrieving_cluster_status"
        );
        console.error(errorMessage);
        this.error.getClusterStatus = errorMessage;
        this.loading.getClusterStatus = false;
        return;
      }
      this.clusterNodes = output.clusterStatus.data.output.nodes;
      this.loading.getClusterStatus = false;
    },
    getNodeLabel(node) {
      let nodeLabel = "";

      if (node.ui_name) {
        nodeLabel =
          node.ui_name +
          " (" +
          this.$t("dashboard.node_id", { id: node.id }) +
          ")";
      } else {
        nodeLabel = this.$t("dashboard.node_id", { id: node.id });
      }

      if (!node.online) {
        return nodeLabel + " [" + this.$t("dashboard.offline") + "]";
      } else {
        return nodeLabel;
      }
    },
    isStartMigrationButtonDisabled(app) {
      return (
        this.loading.migrationUpdate ||
        app.status == "skipped" ||
        (this.emailApp &&
          [
            "nethserver-roundcubemail",
            "nethserver-sogo",
            "nethserver-webtop5",
            "nethserver-mail-getmail"
          ].includes(app.id))
      );
    },
    isMailChild(app) {
      return (
        this.emailApp &&
        [
          "nethserver-roundcubemail",
          "nethserver-sogo",
          "nethserver-webtop5",
          "nethserver-mail-getmail"
        ].includes(app.id)
      );
    },
    isAdChild(app) {
      return app.id == "nethserver-samba";
    }
  }
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

.mg-top-10 {
  margin-top: 10px;
}

.mg-bottom-20 {
  margin-bottom: 20px;
}

.migration-buttons {
  width: 33%;
  display: flex;
  justify-content: flex-end;
}

.node-spinner {
  margin-left: 20px;
}

.skipped {
  filter: grayscale(1);
}
</style>
