#!/usr/bin/env python
import argparse
import os
from jira import JIRA
import sys
import json

#TODO: Move these defautls to config file
config_file_path = os.path.join(os.path.expanduser("~"), ".devconfig")
jira_url = "http://jira"
project_name = "Test EOS"
board_name = "Test EOS"
triage_epic_name = "Production Bugs"
triage_priority_blocker_name = "Blocker"

def triage(args):
    print args
    print "IN TRIAGE"
    print "Issue Key: {0}".format(args.issuekey)
    
    issue_key = args.issuekey
    story_points = args.storypoints
    assignee_name = args.assignee
    
    jira =  JIRA(jira_url, basic_auth=(args.user, args.password))
    issue = jira.issue(issue_key)
    
    #All of this should move to a config file eventually
    #Get field name for Epic Links and assing it to the Epic "Production Bugs"
    #Get Story Points field name and assign points
    #Priority with a value of "Blocker"
    #Assign it to the current Sprint
    
    priority_field_name = None
    story_points_field_name = None
    epic_field_name = None
    sprint_field_name = None
    epic = None
    priority_blocker = None

    for field in jira.fields():
        if field["name"] == "Priority":
            priority_field_name = field["id"]
        if field["name"] == "Story Points":
            story_points_field_name = field["id"]
        if field["name"] == "Epic Link":
            epic_field_name = field["id"]
        if field["name"] == "Sprint":
            sprint_field_name = field["id"]
    
    for p in jira.priorities():
        if p.name == triage_priority_blocker_name:
            priority_blocker = p
            break

    if not priority_blocker:
        print 'Could not find a priority named "Blocker". Issue will not be triaged properly\n'

    epic_issue = jira.search_issues("Project = '{0}' AND issueType = 'Epic' AND 'Epic Name' = '{1}'".format(project_name, triage_epic_name))
    
    if not epic_issue:
        print 'Could not find an Epic named "{0}". Issue will not be assigned to this Epic."\n'.format(triage_epic_name)
    
    #get the current Sprint - DO NOT move this to a config file as this will change often
    #it should always be found on every invocation
    current_sprint = None
    
    board_id = None
    for board in jira.boards():
        if board.name == board_name:
            board_id = board.id
            break
    
    if not board_id:
        print 'Unable to find board "{0}" Will not be able to assign the issue to the active sprint'.format(board_name)
    
    sprint_id = None
    for sprint in jira.sprints(board_id, True):
        if sprint.state == "ACTIVE":
            sprint_id = sprint.id
            break

    if not sprint_id:
        print "Could not find an active sprint. Issue will not be assigned to a sprint."

    data = {}
    #Issue with JIRA API that casues a 500 error if fields are already set
    #Only update that fields that are not set correctly
    if getattr(issue.fields(), priority_field_name).id != str(priority_blocker.id):
        data[priority_field_name] = { "id": str(priority_blocker.id) }

    if getattr(issue.fields(), epic_field_name) != epic_issue[0].key:
        data[epic_field_name] = epic_issue[0].key 

    if getattr(issue.fields(), story_points_field_name) != story_points:
        data[story_points_field_name] = story_points
    
    is_sprint_assigned = False
    sprints =  getattr(issue.fields(), sprint_field_name)
    if sprints:
        for sprint in sprints:
            if sprint.split("id=")[-1].strip("]") == str(sprint_id):
                is_sprint_assigned = True
                break
    
    if not is_sprint_assigned:   
    #if getattr(issue.fields(), sprint_field_name)[0].split("id=")[-1].strip("]") != str(sprint_id):
        data[sprint_field_name] = str(sprint_id)
    
    #TODO: Validate that assignee exists as a user in JIRA
    is_assigned = False
    if issue.fields().assignee:
        if issue.fields().assignee.name == assignee_name:
            is_assigned = True
    
    if not is_assigned:
        data["assignee"] = { "name": assignee_name }

#    data = {
#        priority_field_name: { "id": str(priority_blocker.id) },
#        epic_field_name: epic_issue[0].key,
#        #epic_field_name: epic_issue[0].id,
#        story_points_field_name: story_points,
#        sprint_field_name: str(sprint_id),
#        "assignee": { "name": assignee_name } 
#
#    }

    print data

    issue.update(fields=data)

            #story points
            #customfield_10004=5, 
            #customfield_10300='Production Bugs', 
            #customfield_10219='216'
            #)



def blocker(args):
    print args

def parse_arguments():
    #parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--user', action="store")
    parser.add_argument('--password', action="store")
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
    parser_triage.add_argument("storypoints", type=int, help="estimated Story Points")
    parser_triage.add_argument("assignee", help="JIRA Assignee")
    parser_triage.set_defaults(func=triage)

    parser_blocker = sub_parsers.add_parser("blocker",
            help="create a new JIRA Bug and set its Priority to 'Blocker'")
    parser_blocker.add_argument("-m", "--message") 
    parser_blocker.set_defaults(func=blocker)

    args = parser.parse_args()
    print args 
    args.func(args)

def process():
    parse_arguments()
    #check if config exists. if it doesn't then "init" it
    #create a new command calle dinit to define a new config file and
    #get all the field names required



if __name__ == "__main__":
    process()





