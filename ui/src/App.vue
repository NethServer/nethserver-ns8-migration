<!--
#
# Copyright (C) 2019 Nethesis S.r.l.
# http://www.nethesis.it - nethserver@nethesis.it
#
# This script is part of NethServer.
#
# NethServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or any later version.
#
# NethServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NethServer.  If not, see COPYING.
#
-->

<template>
  <div id="app">
    <nav
      id="navbar-left"
      class="nav-pf-vertical nav-pf-vertical-with-sub-menus nav-pf-persistent-secondary panel-group"
    >
      <ul class="list-group panel">
        <router-link
          tag="li"
          to="/dashboard"
          active-class="active"
          class="list-group-item"
          id="dashboard-item"
        >
          <a>
            <span class="fa fa-cube"></span>
            <span class="list-group-item-value">{{ $t("dashboard.app") }}</span>
          </a>
        </router-link>
        <li class="li-empty"></li>
        <router-link
          tag="li"
          to="/logs"
          active-class="active"
          class="list-group-item"
        >
          <a>
            <span class="fa fa-list"></span>
            <span class="list-group-item-value">{{ $t("logs.title") }}</span>
          </a>
        </router-link>
        <router-link
          tag="li"
          to="/about"
          active-class="active"
          class="list-group-item"
        >
          <a>
            <span class="fa fa-info"></span>
            <span class="list-group-item-value">{{ $t("about.title") }}</span>
          </a>
        </router-link>
      </ul>
    </nav>
    <div class="container-fluid container-cards-pf">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: "App",
  watch: {
    $route: function(val) {
      localStorage.setItem("path", val.path);
    },
  },
  mounted() {
    var path = localStorage.getItem("path") || "/";
    this.$router.push(path);
  },
  methods: {
    getCurrentPath(route, offset) {
      if (offset) {
        return this.$route.path.split("/")[offset] === route;
      } else {
        return this.$route.path.split("/")[1] === route;
      }
    },
  },
};
</script>

<style>
.divider {
  border-bottom: 1px solid #d1d1d1;
}
.v-suggestions .items {
  max-height: 290px;
  overflow-y: hidden;
  border: 1px solid #bbb;
  border-width: 1px;
}
.v-suggestions .suggestions {
  top: 23px;
  background-color: #fff;
  border-radius: 1px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
  font-size: 12px;
  text-align: left;
}

.adjust-top-loader {
  top: 0;
}

.apps-icon {
  height: 30px;
  width: 30px;
}
</style>
