import sys, logging, argparse
import lists.crawl

logging.basicConfig(level=logging.DEBUG)

def run(args):

    if not args.url:
        sys.exit('No url(s). Aborting.')

    if not args.names:
        args.names = []

    ## check valid url?... hmm... nej
    i = 0
    for u in args.url:
        name = args.names[i] if i < len(args.names) else None
        lists.crawl.crawl(u, name, args.arch)
        i = i + 1
    
    sys.exit()

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Mailinglists are dead. Long live mailinglists!')
    p.add_argument('url', metavar="url", help="mailinglist urls to archive", nargs="+")
    p.add_argument('--names', help="mailinglists' names", nargs="+")
    p.add_argument('--arch', help="path to archives directory (default='archives')", default="archives")

    args = p.parse_args()

    run(args)
