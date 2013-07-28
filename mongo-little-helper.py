import pymongo
from optparse import OptionParser
from collections import defaultdict as dd

def get_query_template(query, to_str=True):
    result = {}
    for c in query:
        if c == '$in':
            result[str(c)] = ['_']
        elif isinstance(query[c], dict):
            result[str(c)] = get_query_template(query[c], False)
        else:
            result[str(c)] = '_'
    return str(result).replace("'", '') if to_str else result

def get_stats(db, host, port):
    mongo = pymongo.Connection('mongodb://{host}:{port}/?slaveOk=true'.format(host=host, port=port))
    requests = mongo[db]['system.profile'].find()

    stats = dd(lambda: dd(lambda: {'count': 0, 'tpl': dd(lambda: dd(int))}))
    for request in requests:
        col = request['ns'].replace(db + '.', '')
        op = 'queries' if request['op'] == 'query' else (request['op'] + 's')

        stats[col][op]['count'] += 1
        if 'command' in request:
            template = get_query_template(request['command'])
        elif 'updateobj' in request:
            template = '{%s, %s}' % (get_query_template(request['query']), get_query_template(request['updateobj']))
        elif 'remove' in request or 'query' in request:
            template = get_query_template(request['query'])

        if 'insert' not in request:
            stats[col][op]['tpl'][template]['count'] += 1
            stats[col][op]['tpl'][template]['lock'] += request['lockStats']['timeLockedMicros']['r']
            stats[col][op]['tpl'][template]['lock'] += request['lockStats']['timeLockedMicros']['w']

    return stats

def print_stats(stats):
    find_total_lock = lambda col: sum([col[op]['tpl'][tpl]['lock'] for op in col for tpl in col[op]['tpl']])
    for col in sorted(stats, key=lambda c: find_total_lock(stats[c]), reverse=True):
        print '\033[1;47m%s\033[0m' % col
        print 'Total ' + ', '.join(['%s: %s' % (op, stats[col][op]['count']) for op in sorted(stats[col])])
        for op in ['queries', 'updates', 'removes', 'commands']:
            if op in stats[col]:
                print '\033[1m%s\033[0m' % op.title()
                tpls = stats[col][op]['tpl']
                for tpl in sorted(tpls, key=lambda t: tpls[t]['lock'], reverse=True):
                    print '%s x %s us\t%s' % (tpls[tpl]['count'], tpls[tpl]['lock'] / tpls[tpl]['count'], tpl)
        print

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--db', dest='db', help='database name')
    parser.add_option('--host', dest='host', help='MongoDB host', default='localhost')
    parser.add_option('--port', dest='port', help='MongoDB port', default='27017')
    (options, args) = parser.parse_args()

    if not options.db:
        parser.print_help()
        parser.error('Please specify db name')

    print_stats(get_stats(options.db, options.host, options.port))
