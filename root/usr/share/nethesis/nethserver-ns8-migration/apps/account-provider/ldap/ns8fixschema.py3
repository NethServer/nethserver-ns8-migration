#
# Copyright (C) 2024 Nethesis S.r.l.
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

import sys
import os
import datetime

#
# This dictionary is a summary of the NS8 LDAP schema. Keys are
# objectClass, values are lists of attribute names. The same attribute may
# belong to many classes. When the NS6 and NS7 LDAP is dumped, we must ignore
# unknown attributes such as those belonging to the old Samba LDAP schema.
#
ns8schema = {
    'top': ['objectClass'],
    'extensibleObject': ['objectClass'],
    'alias': ['objectClass', 'aliasedObjectName'],
    'referral': ['objectClass', 'ref'],
    'OpenLDAProotDSE': ['objectClass', 'cn'],
    'subentry': ['objectClass', 'cn', 'subtreeSpecification'],
    'subschema': ['dITStructureRules', 'nameForms', 'dITContentRules', 'objectClasses', 'attributeTypes', 'matchingRules', 'matchingRuleUse'],
    'dynamicObject': ['objectClass'],
    'olcConfig': ['objectClass'],
    'olcGlobal': ['objectClass', 'cn', 'olcConfigFile', 'olcConfigDir', 'olcAllows', 'olcArgsFile', 'olcAttributeOptions', 'olcAuthIDRewrite', 'olcAuthzPolicy', 'olcAuthzRegexp', 'olcConcurrency', 'olcConnMaxPending', 'olcConnMaxPendingAuth', 'olcDisallows', 'olcGentleHUP', 'olcIdleTimeout', 'olcIndexSubstrIfMaxLen', 'olcIndexSubstrIfMinLen', 'olcIndexSubstrAnyLen', 'olcIndexSubstrAnyStep', 'olcIndexHash64', 'olcIndexIntLen', 'olcListenerThreads', 'olcLocalSSF', 'olcLogFile', 'olcLogFileFormat', 'olcLogLevel', 'olcLogFileOnly', 'olcLogFileRotate', 'olcMaxFilterDepth', 'olcPasswordCryptSaltFormat', 'olcPasswordHash', 'olcPidFile', 'olcPluginLogFile', 'olcReadOnly', 'olcReferral', 'olcReplogFile', 'olcRequires', 'olcRestrict', 'olcReverseLookup', 'olcRootDSE', 'olcSaslAuxprops', 'olcSaslAuxpropsDontUseCopy', 'olcSaslAuxpropsDontUseCopyIgnore', 'olcSaslCBinding', 'olcSaslHost', 'olcSaslRealm', 'olcSaslSecProps', 'olcSecurity', 'olcServerID', 'olcSizeLimit', 'olcSockbufMaxIncoming', 'olcSockbufMaxIncomingAuth', 'olcTCPBuffer', 'olcThreads', 'olcThreadQueues', 'olcTimeLimit', 'olcTLSCACertificateFile', 'olcTLSCACertificatePath', 'olcTLSCertificateFile', 'olcTLSCertificateKeyFile', 'olcTLSCipherSuite', 'olcTLSCRLCheck', 'olcTLSCACertificate', 'olcTLSCertificate', 'olcTLSCertificateKey', 'olcTLSRandFile', 'olcTLSVerifyClient', 'olcTLSDHParamFile', 'olcTLSECName', 'olcTLSCRLFile', 'olcTLSProtocolMin', 'olcToolThreads', 'olcWriteTimeout', 'olcObjectIdentifier', 'olcAttributeTypes', 'olcObjectClasses', 'olcDitContentRules', 'olcLdapSyntaxes'],
    'olcSchemaConfig': ['objectClass', 'cn', 'olcObjectIdentifier', 'olcLdapSyntaxes', 'olcAttributeTypes', 'olcObjectClasses', 'olcDitContentRules'],
    'olcBackendConfig': ['objectClass', 'olcBackend'],
    'olcDatabaseConfig': ['objectClass', 'olcDatabase', 'olcDisabled', 'olcHidden', 'olcSuffix', 'olcSubordinate', 'olcAccess', 'olcAddContentAcl', 'olcLastMod', 'olcLastBind', 'olcLastBindPrecision', 'olcLimits', 'olcMaxDerefDepth', 'olcPlugin', 'olcReadOnly', 'olcReplica', 'olcReplicaArgsFile', 'olcReplicaPidFile', 'olcReplicationInterval', 'olcReplogFile', 'olcRequires', 'olcRestrict', 'olcRootDN', 'olcRootPW', 'olcSchemaDN', 'olcSecurity', 'olcSizeLimit', 'olcSyncUseSubentry', 'olcSyncrepl', 'olcTimeLimit', 'olcUpdateDN', 'olcUpdateRef', 'olcMultiProvider', 'olcMonitoring', 'olcExtraAttrs'],
    'olcOverlayConfig': ['objectClass', 'olcOverlay', 'olcDisabled'],
    'olcIncludeFile': ['objectClass', 'olcInclude', 'cn', 'olcRootDSE'],
    'olcFrontendConfig': ['olcDefaultSearchBase', 'olcPasswordHash', 'olcSortVals'],
    'olcModuleList': ['objectClass', 'cn', 'olcModulePath', 'olcModuleLoad'],
    'olcLdifConfig': ['objectClass', 'olcDatabase', 'olcDisabled', 'olcHidden', 'olcSuffix', 'olcSubordinate', 'olcAccess', 'olcAddContentAcl', 'olcLastMod', 'olcLastBind', 'olcLastBindPrecision', 'olcLimits', 'olcMaxDerefDepth', 'olcPlugin', 'olcReadOnly', 'olcReplica', 'olcReplicaArgsFile', 'olcReplicaPidFile', 'olcReplicationInterval', 'olcReplogFile', 'olcRequires', 'olcRestrict', 'olcRootDN', 'olcRootPW', 'olcSchemaDN', 'olcSecurity', 'olcSizeLimit', 'olcSyncUseSubentry', 'olcSyncrepl', 'olcTimeLimit', 'olcUpdateDN', 'olcUpdateRef', 'olcMultiProvider', 'olcMonitoring', 'olcExtraAttrs', 'olcDbDirectory'],
    'olcMonitorConfig': ['objectClass', 'olcDatabase', 'olcDisabled', 'olcHidden', 'olcSuffix', 'olcSubordinate', 'olcAccess', 'olcAddContentAcl', 'olcLastMod', 'olcLastBind', 'olcLastBindPrecision', 'olcLimits', 'olcMaxDerefDepth', 'olcPlugin', 'olcReadOnly', 'olcReplica', 'olcReplicaArgsFile', 'olcReplicaPidFile', 'olcReplicationInterval', 'olcReplogFile', 'olcRequires', 'olcRestrict', 'olcRootDN', 'olcRootPW', 'olcSchemaDN', 'olcSecurity', 'olcSizeLimit', 'olcSyncUseSubentry', 'olcSyncrepl', 'olcTimeLimit', 'olcUpdateDN', 'olcUpdateRef', 'olcMultiProvider', 'olcMonitoring', 'olcExtraAttrs'],
    'olcMdbBkConfig': ['objectClass', 'olcBackend', 'olcBkMdbIdlExp'],
    'olcMdbConfig': ['objectClass', 'olcDatabase', 'olcDisabled', 'olcHidden', 'olcSuffix', 'olcSubordinate', 'olcAccess', 'olcAddContentAcl', 'olcLastMod', 'olcLastBind', 'olcLastBindPrecision', 'olcLimits', 'olcMaxDerefDepth', 'olcPlugin', 'olcReadOnly', 'olcReplica', 'olcReplicaArgsFile', 'olcReplicaPidFile', 'olcReplicationInterval', 'olcReplogFile', 'olcRequires', 'olcRestrict', 'olcRootDN', 'olcRootPW', 'olcSchemaDN', 'olcSecurity', 'olcSizeLimit', 'olcSyncUseSubentry', 'olcSyncrepl', 'olcTimeLimit', 'olcUpdateDN', 'olcUpdateRef', 'olcMultiProvider', 'olcMonitoring', 'olcExtraAttrs', 'olcDbDirectory', 'olcDbCheckpoint', 'olcDbEnvFlags', 'olcDbNoSync', 'olcDbIndex', 'olcDbMaxReaders', 'olcDbMaxSize', 'olcDbMode', 'olcDbSearchStack', 'olcDbMaxEntrySize', 'olcDbRtxnSize', 'olcDbMultival'],
    'olcSyncProvConfig': ['objectClass', 'olcOverlay', 'olcDisabled', 'olcSpCheckpoint', 'olcSpSessionlog', 'olcSpNoPresent', 'olcSpReloadHint', 'olcSpSessionlogSource'],
    'olcDynListConfig': ['objectClass', 'olcOverlay', 'olcDisabled', 'olcDynListAttrSet'],
    'pwdPolicyChecker': ['objectClass', 'pwdCheckModule', 'pwdCheckModuleArg', 'pwdUseCheckModule'],
    'pwdPolicy': ['objectClass', 'pwdAttribute', 'pwdMinAge', 'pwdMaxAge', 'pwdInHistory', 'pwdCheckQuality', 'pwdMinLength', 'pwdMaxLength', 'pwdExpireWarning', 'pwdGraceAuthNLimit', 'pwdGraceExpiry', 'pwdLockout', 'pwdLockoutDuration', 'pwdMaxFailure', 'pwdFailureCountInterval', 'pwdMustChange', 'pwdAllowUserChange', 'pwdSafeModify', 'pwdMinDelay', 'pwdMaxDelay', 'pwdMaxIdle', 'pwdMaxRecordedFailure'],
    'olcPPolicyConfig': ['objectClass', 'olcOverlay', 'olcDisabled', 'olcPPolicyDefault', 'olcPPolicyHashCleartext', 'olcPPolicyUseLockout', 'olcPPolicyForwardUpdates', 'olcPPolicyDisableWrite', 'olcPPolicySendNetscapeControls', 'olcPPolicyCheckModule'],
    'country': ['objectClass', 'c', 'searchGuide', 'description'],
    'locality': ['objectClass', 'street', 'seeAlso', 'searchGuide', 'st', 'l', 'description'],
    'organization': ['objectClass', 'o', 'userPassword', 'searchGuide', 'seeAlso', 'businessCategory', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'telephoneNumber', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'st', 'l', 'description'],
    'organizationalUnit': ['objectClass', 'ou', 'userPassword', 'searchGuide', 'seeAlso', 'businessCategory', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'telephoneNumber', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'st', 'l', 'description'],
    'person': ['objectClass', 'sn', 'cn', 'userPassword', 'telephoneNumber', 'seeAlso', 'description'],
    'organizationalPerson': ['objectClass', 'sn', 'cn', 'userPassword', 'telephoneNumber', 'seeAlso', 'description', 'title', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'ou', 'st', 'l'],
    'organizationalRole': ['objectClass', 'cn', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'telephoneNumber', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'seeAlso', 'roleOccupant', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'ou', 'st', 'l', 'description'],
    'groupOfNames': ['objectClass', 'member', 'cn', 'businessCategory', 'seeAlso', 'owner', 'ou', 'o', 'description'],
    'residentialPerson': ['objectClass', 'sn', 'cn', 'userPassword', 'telephoneNumber', 'seeAlso', 'description', 'l', 'businessCategory', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'st'],
    'applicationProcess': ['objectClass', 'cn', 'seeAlso', 'ou', 'l', 'description'],
    'applicationEntity': ['objectClass', 'presentationAddress', 'cn', 'supportedApplicationContext', 'seeAlso', 'ou', 'o', 'l', 'description'],
    'dSA': ['objectClass', 'presentationAddress', 'cn', 'supportedApplicationContext', 'seeAlso', 'ou', 'o', 'l', 'description', 'knowledgeInformation'],
    'device': ['objectClass', 'cn', 'serialNumber', 'seeAlso', 'owner', 'ou', 'o', 'l', 'description'],
    'strongAuthenticationUser': ['objectClass', 'userCertificate'],
    'certificationAuthority': ['objectClass', 'authorityRevocationList', 'certificateRevocationList', 'cACertificate', 'crossCertificatePair'],
    'groupOfUniqueNames': ['objectClass', 'uniqueMember', 'cn', 'businessCategory', 'seeAlso', 'owner', 'ou', 'o', 'description'],
    'userSecurityInformation': ['objectClass', 'supportedAlgorithms'],
    'certificationAuthority-V2': ['objectClass', 'authorityRevocationList', 'certificateRevocationList', 'cACertificate', 'crossCertificatePair', 'deltaRevocationList'],
    'cRLDistributionPoint': ['objectClass', 'cn', 'certificateRevocationList', 'authorityRevocationList', 'deltaRevocationList'],
    'dmd': ['objectClass', 'dmdName', 'userPassword', 'searchGuide', 'seeAlso', 'businessCategory', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'telephoneNumber', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'st', 'l', 'description'],
    'pkiUser': ['objectClass', 'userCertificate'],
    'pkiCA': ['objectClass', 'authorityRevocationList', 'certificateRevocationList', 'cACertificate', 'crossCertificatePair'],
    'deltaCRL': ['objectClass', 'deltaRevocationList'],
    'labeledURIObject': ['objectClass', 'labeledURI'],
    'simpleSecurityObject': ['objectClass', 'userPassword'],
    'dcObject': ['objectClass', 'dc'],
    'uidObject': ['objectClass', 'uid'],
    'pilotPerson': ['objectClass', 'sn', 'cn', 'userPassword', 'telephoneNumber', 'seeAlso', 'description', 'userid', 'textEncodedORAddress', 'rfc822Mailbox', 'favouriteDrink', 'roomNumber', 'userClass', 'homeTelephoneNumber', 'homePostalAddress', 'secretary', 'personalTitle', 'preferredDeliveryMethod', 'businessCategory', 'janetMailbox', 'otherMailbox', 'mobileTelephoneNumber', 'pagerTelephoneNumber', 'organizationalStatus', 'mailPreferenceOption', 'personalSignature'],
    'account': ['objectClass', 'userid', 'description', 'seeAlso', 'localityName', 'organizationName', 'organizationalUnitName', 'host'],
    'document': ['objectClass', 'documentIdentifier', 'commonName', 'description', 'seeAlso', 'localityName', 'organizationName', 'organizationalUnitName', 'documentTitle', 'documentVersion', 'documentAuthor', 'documentLocation', 'documentPublisher'],
    'room': ['objectClass', 'commonName', 'roomNumber', 'description', 'seeAlso', 'telephoneNumber'],
    'documentSeries': ['objectClass', 'commonName', 'description', 'seeAlso', 'telephonenumber', 'localityName', 'organizationName', 'organizationalUnitName'],
    'domain': ['objectClass', 'domainComponent', 'associatedName', 'organizationName', 'description', 'businessCategory', 'seeAlso', 'searchGuide', 'userPassword', 'localityName', 'stateOrProvinceName', 'streetAddress', 'physicalDeliveryOfficeName', 'postalAddress', 'postalCode', 'postOfficeBox', 'facsimileTelephoneNumber', 'internationalISDNNumber', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'preferredDeliveryMethod', 'destinationIndicator', 'registeredAddress', 'x121Address'],
    'RFC822localPart': ['objectClass', 'domainComponent', 'associatedName', 'organizationName', 'description', 'businessCategory', 'seeAlso', 'searchGuide', 'userPassword', 'localityName', 'stateOrProvinceName', 'streetAddress', 'physicalDeliveryOfficeName', 'postalAddress', 'postalCode', 'postOfficeBox', 'facsimileTelephoneNumber', 'internationalISDNNumber', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'preferredDeliveryMethod', 'destinationIndicator', 'registeredAddress', 'x121Address', 'commonName', 'surname'],
    'dNSDomain': ['objectClass', 'domainComponent', 'associatedName', 'organizationName', 'description', 'businessCategory', 'seeAlso', 'searchGuide', 'userPassword', 'localityName', 'stateOrProvinceName', 'streetAddress', 'physicalDeliveryOfficeName', 'postalAddress', 'postalCode', 'postOfficeBox', 'facsimileTelephoneNumber', 'internationalISDNNumber', 'telephoneNumber', 'teletexTerminalIdentifier', 'telexNumber', 'preferredDeliveryMethod', 'destinationIndicator', 'registeredAddress', 'x121Address', 'ARecord', 'MDRecord', 'MXRecord', 'NSRecord', 'SOARecord', 'CNAMERecord'],
    'domainRelatedObject': ['objectClass', 'associatedDomain'],
    'friendlyCountry': ['objectClass', 'c', 'searchGuide', 'description', 'friendlyCountryName'],
    'pilotOrganization': ['objectClass', 'o', 'userPassword', 'searchGuide', 'seeAlso', 'businessCategory', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'telephoneNumber', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'st', 'l', 'description', 'ou', 'buildingName'],
    'pilotDSA': ['objectClass', 'presentationAddress', 'cn', 'supportedApplicationContext', 'seeAlso', 'ou', 'o', 'l', 'description', 'knowledgeInformation', 'dSAQuality'],
    'qualityLabelledData': ['objectClass', 'dsaQuality', 'subtreeMinimumQuality', 'subtreeMaximumQuality'],
    'posixAccount': ['objectClass', 'cn', 'uid', 'uidNumber', 'gidNumber', 'homeDirectory', 'userPassword', 'loginShell', 'gecos', 'description'],
    # DROP 'shadowAccount': ['objectClass', 'uid', 'userPassword', 'shadowLastChange', 'shadowMin', 'shadowMax', 'shadowWarning', 'shadowInactive', 'shadowExpire', 'shadowFlag', 'description'],
    'posixGroup': ['objectClass', 'cn', 'gidNumber', 'userPassword', 'memberUid', 'description'],
    'ipService': ['objectClass', 'cn', 'ipServicePort', 'ipServiceProtocol', 'description'],
    'ipProtocol': ['objectClass', 'cn', 'ipProtocolNumber', 'description'],
    'oncRpc': ['objectClass', 'cn', 'oncRpcNumber', 'description'],
    'ipHost': ['objectClass', 'cn', 'ipHostNumber', 'l', 'description', 'manager'],
    'ipNetwork': ['objectClass', 'cn', 'ipNetworkNumber', 'ipNetmaskNumber', 'l', 'description', 'manager'],
    'nisNetgroup': ['objectClass', 'cn', 'nisNetgroupTriple', 'memberNisNetgroup', 'description'],
    'nisMap': ['objectClass', 'nisMapName', 'description'],
    'nisObject': ['objectClass', 'cn', 'nisMapEntry', 'nisMapName', 'description'],
    'ieee802Device': ['objectClass', 'macAddress'],
    'bootableDevice': ['objectClass', 'bootFile', 'bootParameter'],
    'inetOrgPerson': ['objectClass', 'sn', 'cn', 'userPassword', 'telephoneNumber', 'seeAlso', 'description', 'title', 'x121Address', 'registeredAddress', 'destinationIndicator', 'preferredDeliveryMethod', 'telexNumber', 'teletexTerminalIdentifier', 'internationalISDNNumber', 'facsimileTelephoneNumber', 'street', 'postOfficeBox', 'postalCode', 'postalAddress', 'physicalDeliveryOfficeName', 'ou', 'st', 'l', 'audio', 'businessCategory', 'carLicense', 'departmentNumber', 'displayName', 'employeeNumber', 'employeeType', 'givenName', 'homePhone', 'homePostalAddress', 'initials', 'jpegPhoto', 'labeledURI', 'mail', 'manager', 'mobile', 'o', 'pager', 'photo', 'roomNumber', 'secretary', 'uid', 'userCertificate', 'x500uniqueIdentifier', 'preferredLanguage', 'userSMIMECertificate', 'userPKCS12'],
    'groupOfURLs': ['objectClass', 'cn', 'memberURL', 'businessCategory', 'description', 'o', 'ou', 'owner', 'seeAlso'],
    'dgIdentityAux': ['objectClass', 'dgIdentity', 'dgAuthz'],
    'namedObject': ['objectClass', 'cn', 'uniqueIdentifier', 'description'],
    'namedPolicy': ['objectClass', 'cn', 'uniqueIdentifier', 'description'],
}


def run_filter():
    ignored_attributes = set()
    ignored_classes = set()
    system_attributes = {
        "dn",
        "structuralObjectClass",
        "entryUUID",
        "creatorsName",
        "createTimestamp",
        "entryCSN",
        "modifiersName",
        "modifyTimestamp",
    }
    def _get_attribute(entry, atname):
        for ea, ev in entry:
            if ea == atname:
                return ev.strip()
        return None
    def _convert_pwd_change_date(epoch_days):
        # change the date format from the number of days since the Unix
        # Epoch to LDAP GeneralizedTime format (restricted ISO8601)
        return datetime.date.fromtimestamp(epoch_days * 86400).strftime('%Y%m%d') + '000000Z'
    def _has_disabled_password(entry):
        for ea, ev in entry:
            if ea == 'userPassword' and ev.startswith(': e0NSWVBUfSE'):
                # The value starts with "{CRYPT}!" in base64 encoding,
                # corresponding to a locked password:
                return True
        return False
    cur_classes = set()
    cur_schema = set()
    cur_entry = []
    for sline in sys.stdin:
        if sline == '\n':
            if cur_classes:
                #
                # Emit entry
                #
                for ea, ev in cur_entry:
                    if ea in system_attributes or ea in cur_schema:
                        print(ea + ':' + ev, end='')
                    else:
                        ignored_attributes.add(ea)
                #
                # Append additional attributes, specific to NS8 schema
                #
                # Convert the last password change timestamp:
                if 'posixAccount' in cur_classes:
                    shadow_last_change = _get_attribute(cur_entry, 'shadowLastChange')
                    if shadow_last_change:
                        try:
                            print('pwdChangedTime: ' + _convert_pwd_change_date(int(shadow_last_change)))
                        except Exception as ex:
                            print('Failed conversion of shadowLastChange with value %s for user %s. Exception details:' % (ev.strip(), _get_attribute(cur_entry, 'uid')), ex, file=sys.stderr)
                # A locked password has a "{CRYPT}!" prefix. If set, copy
                # the information into pwdAccountLockedTime:
                if 'posixAccount' in cur_classes and _has_disabled_password(cur_entry):
                    print("pwdAccountLockedTime: 000001010000Z")
                # NS8 apps require a displayName attribute is set. Copy
                # gecos attribute value to displayName, if it is not
                # already present. If gecos is not available, try with cn
                # or uid.
                if 'inetOrgPerson' in cur_classes and not _get_attribute(cur_entry, 'displayName'):
                    displayName = _get_attribute(cur_entry, 'gecos') or _get_attribute(cur_entry, 'cn') or _get_attribute(cur_entry, 'uid')
                    print("displayName: " + displayName)
                print()
            # Start a new LDIF entry
            cur_classes.clear()
            cur_schema.clear()
            cur_entry.clear()
            continue
        attribute, value = sline.split(':', 1)
        if attribute == 'objectClass':
            clname = value.strip()
            if clname in ns8schema:
                cur_classes.add(clname)
                cur_schema.update(ns8schema[clname])
                cur_entry.append((attribute, value))
            else:
                ignored_classes.add(clname)
        else:
            cur_entry.append((attribute, value))

    print("ns8fixschema.py3 ignored classes:", repr(ignored_classes), file=sys.stderr)
    print("ns8fixschema.py3 ignored attributes:", repr(ignored_attributes), file=sys.stderr)

if __name__ == '__main__':
    run_filter()
