#!/usr/bin/env python
# Copyright (c) 2011 - Alessandro Madruga Correia <amcorreia@zarathustra.com.br>

# Utilizado para apagar todo o historico de conversas do JID fornecido
# plugin do openfire: "Monitoring Service"

import sys

try:
	import adodb
except:
	print 'Nao foi encontrado lib adodb. Execute "apt-get install python-adodb python-psycopg"'
	sys.exit (255)


#   <type_of_db>://<username>:<password>@<host>/<database>
# type_of_db: [postgres|mysql|sqlite|oci8]
conn_string = 'postgres://USERNAME:SENHA@localhost/DATABASE'
conn = None 
__prog_name = None


def help ():
    print '''
    Uso: %s <JID>
    Apaga TODO o historico de conversas do <JID>
    ''' % __prog_name
    sys.exit (0)

# eh tiro curto
def sql_get_res0 (sql):
    cu = conn.Execute (sql)
    return cu.FetchRow ()

# delete ofMessageArchive
def del_ofma (cid):
    sql = 'DELETE FROM ofMessageArchive WHERE conversationid = %s' % cid
    cu = conn.Execute (sql)

# delete ofConParticipant
def del_ofcp (cid):
    sql = 'DELETE FROM ofConParticipant WHERE conversationid = %s' % cid
    cu = conn.Execute (sql)
		
# delete ofConversation
def del_ofc (cid):
    sql = 'DELETE FROM ofConversation WHERE conversationid = %s' % cid
    cu = conn.Execute (sql)

def update_progress(progress):
    sys.stdout.write ("%03d%% concluido\r" % progress)
    sys.stdout.flush ()

# Deleta todas as msg de um determinado jid
def del_all_msg (jid):
    sql = '''SELECT count(conversationID) FROM ofConParticipant WHERE barejid = '%s' ''' % jid
    row = sql_get_res0 (sql)

    if row == None:
        print 'Usuario nao encontrado %s' %jid
        sys.exit (-1)

    count = row[0]

    for idx in range (count):
        sql = '''SELECT conversationID FROM ofConParticipant WHERE barejid = '%s' LIMIT 1''' % jid
        cu  = conn.Execute (sql)
        row = cu.FetchRow ()
        del_ofma (row[0])
        del_ofcp (row[0])
        del_ofc  (row[0])
        perc = (((idx+1)*100) / count)
        update_progress (perc)
    print ''
	
def main (argv):
    global conn
    jid = argv[0]
    try:
        jid.index ('@')
    except ValueError:
        print 'JID incorreto'
        sys.exit (-1)
    conn = adodb.NewADOConnection (conn_string)
    del_all_msg (jid)
    conn.Close ()


if '__main__' == __name__:
    if len (sys.argv) < 2 or sys.argv[1] == '-h':
        help ()
    __prog_name = sys.argv.pop(0)
    main (sys.argv)

