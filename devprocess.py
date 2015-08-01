#!/usr/bin/env python
import argparse
import sys
import json

def triage(args):
    print args

def blocker(args):
    print args

def process():
    #parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    #parser.add_argument("command", choices=["triage", "create"])
    #help="triage a Bug as a Blocker in JIRA")
    sub_parsers = parser.add_subparsers()
    #parser_triage = sub_parsers.add_parser("triage", formatter_class=argparse.RawTextHelpFormatter,
    parser_triage = sub_parsers.add_parser("triage",
            help="triage a JIRA Bug to:\n" \
                "\tset its Priority to 'Blocker'\n" \
                "\tassign it to the 'Production Bugs' Epic\n" \
                "\tmove it to the current Sprint")
    parser_triage.add_argument("issuekey", help="an existing JIRA issue key")
    parser_triage.add_argument("storypoints", help="estimated Story Points")
    parser_triage.add_argument("assignee", help="JIRA Assignee")


    parser_blocker = sub_parsers.add_parser("blocker",
            help="create a new JIRA Bug and set its Priority to 'Blocker'")
    parser_blocker.add_argument("-m", "--message") 
    
    args = parser.parse_args()



if __name__ == "__main__":
    process()





