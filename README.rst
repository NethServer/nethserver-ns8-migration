========================
nethserver-ns8-migration
========================

This package will migrate services from NethServer 7 to NethServer 8 (NS8).

On install the ``nethserver-ns8-migration-update`` event creates a WireGuard private key.
This key is later used to join NS8 cluster as a special node which *can't* be used to run containers.

The ``join-ns8`` script can be used to retrieve Wireguard configuration: ::

  join-ns8 [--no-tlsverify] <ns8_host> <admin_user> <admin_pass>

After executing the ``join-ns8`` command, the ``nethserver-ns8-migration-save`` event will establish
the VPN connection.

Example: ::

  join-ns8 ns8.nethserver.org admin Nethesis,1234
  signal-event nethserver-ns8-migration-save

