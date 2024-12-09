import argparse
import asyncio

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("-c", "--config", dest="config", type=str, default="config.ini")
    argp.add_argument("-s", "--source", dest="source", type=str)
    argp.add_argument("-d", "--destination", dest="destination", type=str)
    argp.add_argument("-i", "--input", dest="input", type=str)
    argp.add_argument("-o", "--output", dest="output", type=str)
    argp.add_argument("--beanstalk-host", dest="beanstalk_host", type=str)
    argp.add_argument("--beanstalk-port", dest="beanstalk_port", type=int)
    argp.add_argument("--bootstrap-servers", dest="bootstrap_servers", type=str)
    argp.add_argument("--nsqd-http-address", dest="nsqd_http_address", type=str)

    argp_sub = argp.add_subparsers(title="action", help="-h / --help to see usage")

    argp_crawler = argp_sub.add_parser("crawler")
    argp_crawler.set_defaults(which="crawler")
    argp_crawler.add_argument("-m", "--mode", dest="mode", type=str)
    argp_crawler.add_argument("-t", "--type", dest="type", type=str)
    argp_crawler.add_argument("-l", "--headless", dest="headless", action="store_true", help="Run in headless mode", default=False)

    args = argp.parse_args()
    if args.which == "crawler":
        if args.type == "eventlist":
            if args.mode == "get_event":
                from controller.eventlist.get_evenlist import RsoeEventlist
                c = RsoeEventlist(**args.__dict__)
                asyncio.run(c.main())