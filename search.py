import sys, logging, argparse
import search.archive

logging.basicConfig(level=logging.DEBUG)

def run(args):

    if not args.keyword:
        sys.exit('No keyword. Aborting.')

    if not args.list:
        args.list = ['spectre', 'crumb', 'empyre'] ## eh....

    for l in args.list:
        arch = search.archive.Archive('archives/')
        arch.load(l)

        r = arch.search(keyword=args.keyword, field=args.field)

        for z in r['results']:
            print(z['thread'] + " ---- " + str(z['nbr_hits']))
            for zz in z['hits']:
                print(" " + zz['url'])
                print(" " + zz['index_str'])

    sys.exit()

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Searches mailinglists archives')
    p.add_argument('keyword', metavar="keyword", help="keyword to search")
    p.add_argument('--list', help="mailinglist(s') name(s)", nargs="+")
    p.add_argument('--field', help="message field (i.e. 'content' or 'subject', etc.)", default="content")

    args = p.parse_args()

    run(args)
