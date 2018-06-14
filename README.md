# LDAP-and-Kerberos-user-management
This utility uses CLI keys:<br/>
-add/--createkrb <USERNAME> <NEWPASS> - adding principal<br/>
Example: ./connector_ldap_kdc.py -add alex qwerty123<br/><br/>
-chpasskrb <USERNAME> <NEWPASS> - changing principal's password<br/>
Example: ./connector_ldap_kdc.py -chpasskrb alex passw0rd<br/><br/>
-chpass <USERNAME> <OLDPASS> <NEWPASS> - changing LDAP user's password and principal's password<br/>
Example: ./connector_ldap_kdc.py -chpass alex qwerty123 passw0rd<br/><br/>
-lock/--lockkrb <USERNAME> - locking user<br/>
Example: ./connector_ldap_kdc.py -lock alex<br/><br/>
-unlock/--unlockkrb <USERNAME> - unlocking user<br/>
Example: ./connector_ldap_kdc.py -unlock alex<br/><br/>
To run the program, you need configure yaml ./connector_ldap_kdc_conf.yaml.<br/>
Example:<br/>
LDAP_URL: \"ldap:///\"<br/>
LDAP_ADM: \"cn=admin,dc=test,dc=local\"<br/>
LDAP_ADM_PASSW: \"passw0rd\"\n\rDC: \"dc=test,dc=local\"<br/>
REALM: \"TEST.LOCAL\"<br/>
PRINCIPAL_OU: \"cn=TEST.LOCAL,cn=kerberos,ou=kdcroot\"
