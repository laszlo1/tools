#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple MyBenefit's product lookup tool.
#
# github.com/laszlo1
#

import sys
import mechanize
import re
import argparse
import getpass


class PasswdPromptAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest=None,
                 nargs=0,
                 default=None,
                 required=False,
                 type=None,
                 metavar=None,
                 help=None):
        super(PasswdPromptAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            required=required,
            type=type,
            metavar=metavar,
            help=help)

    def __call__(self, parser, args, values, option_strings=None):
        passwd = getpass.getpass()
        setattr(args, self.dest, passwd)


def check_mybenefit(username, passwd, company, product, verbose):
    browser = mechanize.Browser(factory=mechanize.RobustFactory())
    browser.set_debug_http(verbose)
    url = 'https://system.mybenefit.pl/mybenefit/login.html'
    browser.addheaders = [
        ( 'User-Agent', '''Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:35.0)
				 Gecko/20100101 Firefox/35.0'''),
        ('Referer', 'https://system.mybenefit.pl/mybenefit/login.html'),
        ( 'Host', '''system.mybenefit.pl'''),
        ( 'Accept', '''text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'''),
        ( 'Accept-Language', '''en-US,en;q=0.5'''),
    ]

    browser.open(url)
    browser.select_form(nr=0)
    browser.form.set_all_readonly(False)
    browser.form['j_username_input'] = username
    browser.form['j_password'] = passwd
    browser.form['j_context'] = company
    browser.form['j_username'] = '||'.join([username, company])

    result = browser.submit()
    url_points_realization = 'https://system.mybenefit.pl/mybenefit/bankpoints-realization.html'
    if re.search('<h2>Podaj login, hasło i nazwę swojej firmy</h2>',
                 result.get_data()):
        print '[!] Login failed!'
        return False

    points_realization = browser.open(url_points_realization)
    if re.search(product, points_realization.read()):
        print "[+] Product: \"%s\" was found !" % product
    else:
        print '[+] Nothing found.'

    if verbose:
        print result.get_data()


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group('Check offer')
    group.add_argument("-o", "--offering", type=str,
                       help="Offering/product name")
    group.add_argument("-u", "--username", type=str, help="User name")
    group.add_argument(
        "-p",
        "--password",
        type=str,
        help="Prompt for the password",
        action=PasswdPromptAction)
    group.add_argument("-c", "--company", type=str, help="Company name")

    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose mode",
        default=False,
        action='store_true')

    args = parser.parse_args()
    if args.offering and args.username and args.password and args.company:
        return check_mybenefit(args.username, args.password,
                               args.company, args.offering, args.verbose)
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main())
