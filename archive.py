import sys, logging, argparse
import lists

logging.basicConfig(level=logging.DEBUG)

def run(args):

    if not args.url:
        sys.exit('No url(s). Aborting.')

    ## check valid url?... hmm... nej
    for u in args.url:
        lists.crawl.crawl(u)
    
    sys.exit()

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Mailinglists are dead. Long live mailinglists!')
    p.add_argument('url', metavar="url", help="mailinglist urls to archive", nargs="+")
    p.add_argument('--arch', help="path to archives directory (default='archives')", default="archives")

    args = p.parse_args()

    run(args)
