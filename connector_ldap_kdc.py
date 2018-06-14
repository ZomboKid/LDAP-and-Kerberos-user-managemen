#! /usr/bin/python

import argparse,sys

#used for direct database access as local root account
import kadmin_local as kadmin

import ldap
import ldap.modlist as modlist

import datetime

import yaml
#-------------------------------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(usage="\n\rBefore using the utility, first configure the configuration YAML file ./connector_ldap_kdc_conf.yaml\n\rExample:\n\rLDAP_URL: \"ldap:///\"\n\rLDAP_ADM: \"cn=admin,dc=test,dc=local\"\n\rLDAP_ADM_PASSW: \"passw0rd\"\n\rDC: \"dc=test,dc=local\"\n\rREALM: \"TEST.LOCAL\"\n\rPRINCIPAL_OU: \"cn=TEST.LOCAL,cn=kerberos,ou=kdcroot\"\n\r\n\r-add/--createkrb <USERNAME> <NEWPASS> - adding principal\n\rExample: ./connector_ldap_kdc -add ivanov qwerty123\n\r\n\r-chpasskrb <USERNAME> <NEWPASS> - changing principal's password\n\rExample: ./connector_ldap_kdc -chpasskrb ivanov passw0rd\n\r\n\r-chpass <USERNAME> <OLDPASS> <NEWPASS> - changing LDAP user's password and principal's password\n\rExample: ./connector_ldap_kdc.py -chpass ivanov qwerty123 passw0rd\n\r\n\r-lock/--lockkrb <USERNAME> - locking user\n\rExample: ./connector_ldap_kdc -lock ivanov\n\r\n\r-unlock/--unlockkrb <USERNAME> - unlocking user\n\rExample: ./connector_ldap_kdc -unlock ivanov")

parser.add_argument("-add","--createkrb",nargs=2,type=str,action="store", help=argparse.SUPPRESS)
parser.add_argument("-chpasskrb","--chpasskrb",nargs=2,type=str,action="store", help=argparse.SUPPRESS)
parser.add_argument("-chpass","--chpass",nargs=3,type=str,action="store", help=argparse.SUPPRESS)
parser.add_argument("-lock","--lockkrb",nargs=1,type=str,action="store", help=argparse.SUPPRESS)
parser.add_argument("-unlock","--unlockkrb",nargs=1,type=str,action="store", help=argparse.SUPPRESS)
#-------------------------------------------------------------------------------------------------------------------------------------------
if len(sys.argv)<2:
    parser.print_help(sys.stderr)
    sys.exit(1)
#-------------------------------------------------------------------------------------------------------------------------------------------
#read config from yaml file './connector_ldap_kdc_conf.yaml'
config_file=open("./connector_ldap_kdc_conf.yaml")
cfg = yaml.load(config_file)

LDAP_URL = (cfg['LDAP_URL'])
LDAP_ADM =  (cfg['LDAP_ADM'])
LDAP_ADM_PASSW = (cfg['LDAP_ADM_PASSW'])
DC = (cfg['DC'])
REALM = (cfg['REALM'])
PRINCIPAL_OU = (cfg['PRINCIPAL_OU'])
#-------------------------------------------------------------------------------------------------------------------------------------------
# Adding principal
def f_add (USERNAME,NEWPASS):
#using 'import kadmin_local as kadmin'
#used for direct database access as local root account
    kadm = kadmin.local()
    kadm.add_principal(USERNAME+"@"+REALM, NEWPASS)
#-------------------------------------------------------------------------------------------------------------------------------------------
# Changing principal's password
def f_chpass_krb (USERNAME,NEWPASS):
#using 'import kadmin_local as kadmin'
#used for direct database access as local root account
    kadm = kadmin.local()
    princ = kadm.getprinc(USERNAME)
    princ.change_password(NEWPASS)
#-------------------------------------------------------------------------------------------------------------------------------------------
# Changing LDAP user's password
def f_chpass_ldap (URL,DN,OLDPASS,NEWPASS):
    conn = ldap.initialize(URL)
    conn.simple_bind_s(DN,OLDPASS)
    ldif=[(ldap.MOD_REPLACE, 'userPassword', NEWPASS )] 
    conn.modify_s(DN,ldif)
    conn.unbind_s()
#-------------------------------------------------------------------------------------------------------------------------------------------
def get_DN (USERNAME):
    conn = ldap.initialize(LDAP_URL)
    conn.simple_bind_s(LDAP_ADM,LDAP_ADM_PASSW)

    base=DC
    criteria="(&(objectClass=posixAccount)(uid="+USERNAME+"))"

    attributes=None
    result = conn.search_s(base, ldap.SCOPE_SUBTREE, criteria, attributes)
    conn.unbind_s()

    return str(result[0][0])
#-------------------------------------------------------------------------------------------------------------------------------------------
def f_chpass (USERNAME,OLDPASS,NEWPASS):
 
    USER_DN=get_DN(USERNAME)

    f_chpass_ldap (LDAP_URL,USER_DN,OLDPASS,NEWPASS)
    f_chpass_krb (USERNAME,NEWPASS)
#-------------------------------------------------------------------------------------------------------------------------------------------
# Locking user
def f_lock (USERNAME):
#this 'if-else' is legacy from bash script command: 'ou=${2:+",${2}"}'
    if PRINCIPAL_OU != "":
        dn="krbPrincipalName="+USERNAME+"@"+REALM+","+PRINCIPAL_OU+","+DC
    else:
        dn="krbPrincipalName="+USERNAME+"@"+REALM+","+DC

    conn = ldap.initialize(LDAP_URL)
    conn.simple_bind_s(LDAP_ADM,LDAP_ADM_PASSW)

#get timestamp for kerberos field 'krbLastFailedAuth'
    timestamp = datetime.datetime.now()
    krb_field=timestamp.strftime('%Y%m%d%H%M%S')+"Z"
#modify ldap attributes
    mod_attrs=[(ldap.MOD_REPLACE,'krbLoginFailedCount',str(10)),(ldap.MOD_REPLACE,'krbLastFailedAuth',krb_field)]
    conn.modify_s(dn, mod_attrs)

    conn.unbind_s()

#-------------------------------------------------------------------------------------------------------------------------------------------
# Unlocking user
def f_unlock (USERNAME):
#this 'if-else' is legacy from bash script command: 'ou=${2:+",${2}"}'
    if PRINCIPAL_OU != "":
        dn="krbPrincipalName="+USERNAME+"@"+REALM+","+PRINCIPAL_OU+","+DC
    else:
        dn="krbPrincipalName="+USERNAME+"@"+REALM+","+DC

    conn = ldap.initialize(LDAP_URL)
    conn.simple_bind_s(LDAP_ADM,LDAP_ADM_PASSW)

#modify ldap attributes
    mod_attrs=[(ldap.MOD_REPLACE,'krbLoginFailedCount',str(0))]
    conn.modify_s(dn, mod_attrs)

    conn.unbind_s()

#-------------------------------------------------------------------------------------------------------------------------------------------
args = parser.parse_args()
if args.createkrb:
    f_add (args.createkrb[0],args.createkrb[1])
elif args.chpasskrb:
    f_chpass_krb(args.chpasskrb[0],args.chpasskrb[1])
elif args.chpass:
    f_chpass(args.chpass[0],args.chpass[1],args.chpass[2])  
elif args.lockkrb:
    f_lock(args.lockkrb[0])
elif args.unlockkrb:
    f_unlock(args.unlockkrb[0])
