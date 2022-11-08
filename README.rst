========================
nethserver-ns8-migration
========================

This package will migrate services from NethServer 7 to NethServer 8 (NS8).

On install the ``nethserver-ns8-migration-update`` event creates a WireGuard private key.
This key is later used to join NS8 cluster as a special node which *can't* be used to run containers.

The ``ns8-join`` command can be used to retrieve Wireguard configuration: ::

  ns8-join [--no-tlsverify] <ns8_host> <admin_user> <admin_pass>

During ``ns8-join`` execution, the ``nethserver-ns8-migration-save`` event
establishes the VPN connection.

Once the VPN is established:

- subsequent NS8 API calls are routed through it
- a temporary NS8 external user domain is created

Example: ::

  ns8-join ns8.nethserver.org admin Nethesis,1234
  signal-event nethserver-ns8-migration-save


After the join, it is possible to execute actions: ::

  ns8-action <agent> <action> <json_data>

Example: ::

  ns8-action cluster get-cluster-status '{}'

The ``ns8-leave`` command can be run when all ns7 modules are successfully migrated to ns8. That script,

- removes the temporary external user domain
- removes the ns7 node account
- stops the Wireguard VPN and cleans up its settings

Migration APIs
==============

The API responsible for apps migration is ``api/migration/update``. To initialize app migration this API can be invoked with ``action: "start"`` or ``action: "sync"``. The API will call the following script: ::

  /usr/share/nethesis/nethserver-ns8-migration/apps/$app/export &>>/var/log/ns8-migration.log

where ``$app`` variable contains the name of a directory named after the app to migrate.

Note that script ``stdout`` and ``stderr`` are redirected to the log file ``/var/log/ns8-migration.log``.

To finalize app migration ``api/migration/update`` can be invoked with ``action: "finish"``. In this case the API will execute: ::

  echo "$migration_config" | /usr/share/nethesis/nethserver-ns8-migration/apps/$app/migrate &>>/var/log/ns8-migration.log

where ``$migration_config`` variable possibly contains a json object that contains some configuration data needed to finalize app migration.
For instance, let's consider Nextcloud migration: if Nextcloud installation on NS7 is not configured with a virtual host, then ``$migration_config`` will contain the name of the Nextcloud virtual host that will be used on NS8 (since virtual host is mandatory on NS8).

After the execution of ``migrate`` script, the migrated app will be stopped and disabled in NS7.


Nextcloud migration
===================

The migration only supports Nextcloud configured with a virtual host inside NS7.
At the end, the migrated Nextcloud install will be accessible at the same virtual host on the remote NS8 cluster.

Assumptions:
- nextcloud is connected to the local Samba AD

Steps:

1. After the ns8-join, configure ldapproxy to connect to local Samba AD: ::

      /usr/share/nethesis/nethserver-ns8-migration/apps/ldapproxy/export

2. The first time, install a Nextcloud instance to NS8. Then synchronize data, configuration and database: ::

     /usr/share/nethesis/nethserver-ns8-migration/apps/nextcloud/export

   This command can be executed multiple times to sync the data until Nextcloud is ready to be totally migrated.

3. When ready for the final migration, execute: ::

     /usr/share/nethesis/nethserver-ns8-migration/apps/nextcloud/migrate

Mattermost migration
====================

At the end, the migrated Mattermost installation will be accessible at the same virtual host on the remote NS8 cluster.

Assumptions:
- Mattermost community edition

Steps:

1. The first time, install a Mattermost instance to NS8. Then synchronize data, configuration and database: ::

     /usr/share/nethesis/nethserver-ns8-migration/apps/mattermost/export

   This command can be executed multiple times to sync the data until Mattermost is ready to be totally migrated.

3. When ready for the final migration, execute: ::

     /usr/share/nethesis/nethserver-ns8-migration/apps/mattermost/migrate
