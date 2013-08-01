#!/usr/bin/env python
'''
   Copyright (c) 2011-2013 - Alessandro Madruga Correia <amcorreia@zarathustra.com.br>
  	The Regents of the University of California.  All rights reserved.
  
   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:
   1. Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
   3. All advertising materials mentioning features or use of this software
      must display the following acknowledgement:
  	This product includes software developed by the University of
  	California, Berkeley and its contributors.
   4. Neither the name of the University nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.
  
   THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
   OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
   SUCH DAMAGE.
'''
 
# Utilizado para apagar todo o historico de conversas do JID fornecido
# plugin do openfire: "Monitoring Service"


import sys
import time

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
    print '''Usage: %s COMMAND [ DATE ]
Where COMMAND = { l[ist] | d[elete] }
      DATE    = [ date_begin DATE_VALUE | date_end DATE_VALUE ]
      DATE_VALUE = [ dd/mm/yy | dd/mm/yy HH:MM ]

    list JID      Lista o historico de conversas do JID
    delete JID    Deleta o historico de conversas do JID
    ''' %  __prog_name
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

def parse_date (argv):
    tm_start = 0
    tm_stop = 0
    idx = 0

    while idx <= (len(argv)-1):
        if argv[idx] == 'date_begin':
            tm_start = argv[idx+1]
        if argv[idx] == 'date_end':
            tm_stop = argv[idx+1]
        idx = idx + 1
 
    #print 'list %s I %s F %s' % (jid,tm_start, tm_stop)
    if tm_start == 0:
        tm_start = int(time.mktime(time.strptime("01/01/1970 00:00", "%d/%m/%Y %H:%M"))) * 1000;
    else:
        try:
            tm_start = int(time.mktime(time.strptime(tm_start, "%d/%m/%Y %H:%M"))) * 1000;
        except:
            tm_start = int(time.mktime(time.strptime(tm_start, "%d/%m/%Y"))) * 1000;
 
    if tm_stop == 0:
        tm_stop = int(time.time()*1000)
    else:
        try:
            tm_stop  = int(time.mktime(time.strptime(tm_stop, "%d/%m/%Y %H:%M"))) * 1000;
        except:
            tm_stop  = int(time.mktime(time.strptime(tm_stop, "%d/%m/%Y"))) * 1000;
    return { 'tm_start' : tm_start, 'tm_stop' : tm_stop }
 
 
# COMMANDS
def cmd_list (argv):
    jid = argv.pop(0)
    tm = parse_date (argv)
    tm_start = tm['tm_start']
    tm_stop  = tm['tm_stop']
    conn = adodb.NewADOConnection (conn_string)
 
    sql = '''SELECT * FROM ofmessagearchive WHERE sentdate > %d and sentdate < %d and (fromjid like '%%%s%%' or tojid like '%%%s%%') ORDER BY sentdate''' % (tm_start, tm_stop, jid, jid)
    cu  = conn.Execute (sql)
    while not cu.EOF:
        arr = cu.GetRowAssoc(0) # 0 is lower, 1 is upper-case
        print '%s %s -> %s:  %s' % ( time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(int(arr['sentdate']/1000))) , arr['fromjid'].split('/')[0], arr['tojid'].split('/')[0], arr['body'])
        cu.MoveNext()
    conn.Close ()
    #print 'list %s I %s F %s XXXX %s %s' % (jid,tm_start, tm_stop, T['tm_start'], T['tm_stop'])


def cmd_delete (argv):
    jid = argv[1]
    try:
        jid.index ('@')
    except ValueError:
        print 'JID incorreto'
        sys.exit (-1)
    conn = adodb.NewADOConnection (conn_string)
    del_all_msg (jid)
    conn.Close ()


def main (argv):
    global conn
    cmd = argv.pop(0)
    if len (argv) < 1:
        print 'Faltam parametros'
        sys.exit (-1)

    if cmd in ['list', 'l']:
       cmd_list (argv)

    elif cmd in ['delete', 'd']:
       cmd_delete (argv)

    else:
       help ()


if '__main__' == __name__:
    __prog_name = sys.argv.pop(0)
    if len (sys.argv) < 1 or sys.argv[0] in ['-h', 'h', 'help']:
        help ()
    main (sys.argv)

