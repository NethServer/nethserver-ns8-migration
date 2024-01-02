========================
nethserver-ns8-migration
========================

This package will migrate services from NethServer 7 to NethServer 8 (NS8).

On install, the ``nethserver-ns8-migration-update`` event creates a
WireGuard private key. This key is later used to join the NS8 cluster VPN.

The ``ns8-join`` command adds NS7 to the cluster VPN and retrieves the its
configuration: ::

  ns8-join [--no-tlsverify] <ns8_host> <admin_user> <admin_pass>

During ``ns8-join`` execution, the ``nethserver-ns8-migration-save`` event
establishes the VPN connection.

Once the VPN is established:

- subsequent NS8 API calls are routed through it
- a temporary NS8 external user domain is created

.. warning::
   The NS8 cluster must be new, with no user domains and installed modules

Example: ::

  ns8-join ns8.nethserver.org admin Nethesis,1234

After the join, it is possible to execute actions: ::

  ns8-action <agent> <action> <json_data>

Example: ::

  ns8-action cluster get-cluster-status '{}'

When NS7 modules are successfully migrated to NS8, run the ``ns8-leave``
command. ::

  ns8-leave

That command:

- ensures the temporary external user domain is removed
- removes the NS7 node from the VPN
- stops the Wireguard VPN and cleans up its settings

Commands
========

This is the full list of commands provided by the tool. They are used by
applications and APIs:

- ``ns8-join`` 
- ``ns8-leave``
- ``ns8-action``
- ``ns8-bind-app``
- ``ns8-abort``

Logs
====

- The trace of bind and migrate procedures is sent to `/var/log/ns8-migration.log`. This log file can be read also from the UI interface and is the most important for troubleshooting.
- E-smith events, installation/uninstallation and related command output is recorded by `/var/log/messages`, as usual.
- On the NS8 destination cluster, look at the destination application log. The invoked module actions are tipically `import-module` and `configure-module`.

Applications
============

The migration tool can migrate a pre-defined set of NS7 applications (apps):

- nethserver-mail (with nethserver-webtop5, nethserver-roundcubemail, nethserver-sogo)
- nethserver-mail-getmail
- nethserver-nextcloud
- nethserver-mattermost
- nethserver-ejabberd
- account-provider (both local AD and LDAP)

Each application has two directories

1. sources (or install) directory with the migration implementation, under
   ``/usr/share/nethesis/nethserver-ns8-migration/apps/``.

2. state directory, with current migration state information, under
   ``/var/lib/nethserver/nethserver-ns8-migration/``

The app sources directory must provide the following files, and implement
the described behavior:

1. ``bind.env``, basic environment variables for the ``bind`` command.

   * ``MODULE_IMAGE_URL`` the Podman image URL to install and start on
     the remote module

   * ``MODULE_VOLUMES`` a list of name of Podman volumes that are created
     by the bind command on the remote side. These volumes can be filled
     by rsync uploads, together with the remote module ``state/``
     directory.

2. ``bind`` command. This command creates a remote NS8 module instance and
   saves the Rsync configuration in the app state directory.

3. ``migrate`` command. This command synchronizes the local application
   configuration and data with the remote Rsync endpoint. If it is passed
   the ``MIGRATE_ACTION=finish`` environment variable, it also finalizes
   the migration: it stops the local services and starts the remote ones.

Optionally the app can provide `jq` input translation filters for the
migration APIs:

- ``input-start.jq``
- ``input-finish.jq``

The filter output is Bash-eval'ed and must define additional environment
variables for the app ``migrate`` command.

Applications can read additional environment files, provided by the RPM
package or created at runtime by the tool commands: ::

  /etc/nethserver/agent.env
  /var/lib/nethserver/nethserver-ns8-migration/agent.env
  /var/lib/nethserver/nethserver-ns8-migration/environment

Nextcloud migration
-------------------

Bind command example ::

  MODULE_NODE_ID=1 ./bind

Sync command example ::

  ./migrate

Finish command example ::

  MIGRATE_ACTION=finish NEXTCLOUD_VHOST=nc.example.com ./migrate

Ejabberd migration
--------------------

Bind command example ::

  MODULE_NODE_ID=1 ./bind

Sync command example ::

  ./migrate

Finish command example ::

  MIGRATE_ACTION=finish ./migrate

Mattermost migration
--------------------

Bind command example ::

  MODULE_NODE_ID=1 ./bind

Sync command example ::

  ./migrate

Finish command example ::

  MIGRATE_ACTION=finish MATTERMOST_VHOST=mattermost.example.com ./migrate

Email, Webtop, Roundcube migration, POP3/IMAP Connector, SOGO
-------------------------------------------------------------

As POP3/IMAP Connector, Webtop and Roundcube depend on the Email application, the
migration of the four modules must occur at the same time and is
controlled by the nethserver-mail app.

Bind command example ::

  MODULE_NODE_ID=1 WEBTOP_NODE_ID=1 ROUNDCUBE_NODE_ID=2 GETMAIL_NODE_ID=1 SOGO_NODE_ID=1 ./bind

Sync command example ::

  ./migrate

Finish command example ::

  MIGRATE_ACTION=finish WEBTOP_VHOST=webtop.example.com ROUNDCUBE_VHOST=rc.example.com SOGO_VHOST=sogo.example.com ./migrate

Just for environment var reference, to finalize nethserver-sogo alone ::

  MIGRATE_ACTION=finish MAIL_INSTANCE_ID=mail1 SOGO_VHOST=sogo.example.com ./migrate

Just for environment var reference, to finalize nethserver-webtop5 alone ::

  MIGRATE_ACTION=finish MAIL_INSTANCE_ID=mail1 WEBTOP_VHOST=webtop.example.com ./migrate

Finally, to finalize nethserver-roundcubemail alone ::

  MIGRATE_ACTION=finish MAIL_INSTANCE_ID=mail1 ROUNDCUBE_VHOST=rc.example.com ./migrate


Account provider
----------------

This application migrates the local account provider. Both AD and LDAP are
handled. External account provider is not migrated: it must be manually
configured in NS8 to reach the same LDAP server used by NS7.


File server
-----------

The Samba file server migration is part of Samba Account provider
migration. It occurs unless the ``skip`` flag is set for the
``nethserver-samba`` application.


Migration APIs
==============

The API responsible for apps migration is ``api/migration/update``. Its
basic input payload format is ::

  {
    "app": "nethserver-testapp",
    "action": "start",
    "migrationConfig": {
      "appNode": 3
    }
  }

It accepts the following ``action`` values for each NS7 module: ``start``,
``sync``, ``finish``, ``abort``.

1. ``start``. Creates one module instance in the NS8 cluster. The local
   NS7 app ``bind`` script is called. Multiple destination modules are
   allowed too: for instance the nethserver-mail app controls the
   migration of nethserver-webtop5 and nethserver-roundcubemail, nethserver-sogo if they
   are installed.

2. ``sync``. Synchronizes local app configuration and data with the remote
   module instance, by calling its ``migrate`` script.

3. ``finish``. Completes the migration by calling the app ``migrate``
   script with the special environment variable ``MIGRATE_ACTION=finish``.

4. ``abort``. Abort module migration. Remove module from NS8 cluster
   and cleanup local stace.

After the execution of the ``finish`` action the app is stopped and
disabled in NS7.

The API ``api/migration/read`` returns the current migration status, for
each known app: ::

  echo '{"action":"listApps"}' | /usr/libexec/nethserver/api/nethserver-ns8-migration/migration/read

Package uninstallation
======================

To remove the tool and its dependencies (if they are not required by other packages): ::

  yum remove nethserver-ns8-migration kmod-wireguard wireguard-tools

Clean up configuration database: ::

  config delete wg-quick@ns8
  config delete ns8

Post-migration step back
========================

Once a service has been migrated to the remote NS8 host it should not run
any more on NS7. When the ``migrate`` command completes the application
services are stopped and disabled.

Please note that some migrated applications may also add some custom templates.
To list such template fragments use: ::

  grep -lR ns8migration /etc/e-smith/templates-custom/


It is possible to manually re-enable the services with the following commands.

::

  # Mail
  config setprop dovecot status enabled
  config setprop postfix status enabled
  config setprop rspamd status enabled
  config setprop opendkim status enabled
  config setprop olefy status enabled

  # Webtop
  config setprop tomcat8@webtop status enabled

  # Roundcube
  config delprop roundcubemail migration

  # SOGo
  config delprop sogod migration
  config setprop sogod status enabled

  # Mattermost
  config setprop mattermost status enabled
  rm -rf /etc/e-smith/templates-custom/etc/httpd/conf.d/zz_mattermost.conf
  signal-event nethserver-mattermost-update

  # Nextcloud
  rm -rf /etc/e-smith/templates-custom/etc/httpd/conf.d/zz_nextcloud.conf
  rm -f /etc/e-smith/templates-custom/etc/httpd/conf.d/default-virtualhost.inc/40nextcloud
  signal-event nethserver-nextcloud-update

  # Account provider
  config setprop slapd status enabled
  config setprop nsdc status enabled
  config setprop sssd status enabled

  # File server
  config setprop smb status enabled
  config setprop smb nmb enabled
  config setprop smb winbind enabled

  # All modules
  signal-event nethserver-ns8-migration-update
  signal-event runlevel-adjust
  signal-event firewall-adjust

Migration notes
===============

.. warning::

  Read carefully the sections below before finishing the migration of any application.

Webtop
------

If you purchased a Webtop license for additional custom fields or other
components/integrations the following additional and manual steps are needed:

1. Before finishing the Mail app migration, access the Webtop
   administrative page and disable any subscribed license.

2. Finish the Mail app migration.

3. In the NS8 module, access the administrative page and enable the
   licenses again.

File server
-----------

File server migration (shared folders) is an optional step of the Samba
account provider migration. It can be performed if the NS8-based DC IP
address is in a private network and is routable from the NS7-based DC.

The NS8 DC cannot be assigned the cluster VPN IP address.

.. warning::

  Exposing SMB and other AD services to public networks is dangerous.


Account provider
----------------

When the migration finishes, the local account provider (both AD and LDAP)
is stopped and disabled. In this state, SSSD allows logging on the system
with its local cache. If some services are left on the system it is
necessary to remove the local account provider and configure NS8 as the
remote account provider.
