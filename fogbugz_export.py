import csv
import os
import time
from datetime import datetime
from decimal import Decimal

from fogbugz import FogBugz
from jira import JIRA
import fbSettings
import jiraSettings

csvfile = ''
flatfile = ''


class FogbugzExport:
    def __init__(self):

        self.fb_dict = {}
        self.description = ''
        self.fb = FogBugz(fbSettings.URL, fbSettings.TOKEN)

        self.response = self.fb.search(
            # q="37549,38765,38270,38559,38741",
            # q="opened:1/14/2013",
            #q="Milestone:30.2",
            #q="38667",
            #q='Milestone:"Undecided"',
            #q='project:"002:FLM" Milestone:"Undecided"',
            #q='project:"012:IT-Operations"',
            #q='project:"000:Salesforce Cases"',
            q='project:"007:MAX" opened:"3/10/2015..1/12/2017"',
            cols="sCategory,ixBug,nFixForOrder,sTitle,dblStoryPts,sPriority,sStatus,sPersonAssignedTo,"
                 "tags,sFixFor,dtOpened,sProject,plugin_customfields_at_fogcreek_com_qaxbuddyf611,"
                 "ixPersonOpenedBy,plugin_customfields_at_fogcreek_com_salesforcexcaseq17,dtDue,"
                 "plugin_customfields_at_fogcreek_com_hotfixp3b,ixPersonResolvedBy,"
                 "sPersonResolvedBy,hrsOrigEst,hrsCurrEst,dtResolved,dtClosed,sArea,"
                 "ixBugChildren,ixBugParent,events")


        #options = {'server': jiraSettings.URL}
        #jira = JIRA(options, basic_auth=(jiraSettings.USER_NAME, jiraSettings.PASSWORD))

        #new_issue = jira.create_issue(project='TES', summary='New issue from jira-python',
         #                             description='Look into this one', issuetype={'name': 'Bug'} )

        # Find all issues reported by the admin
        #issues = jira.search_issues('assignee=Bill Rogalla')
        #issue = jira.issue('TES-38667')
        #self.write_fields_to_csv_file(response)
        #  write response to csv file


    def get_milestones_by_project_id(self):
        projResp = self.fb.listProjects()

        for project in projResp.projects.childGenerator():
            milestoneResp = self.fb.listFixFors(project.ixProject.string)
            print("--------------------------------")
            print("project: " + project.sFixFor.string + "\n")
            print("--------------------------------")
            print("milestones: ")
            for milestone in milestoneResp.fixfors.childGenerator():
                print(milestone.sFixFor.string)

    def read_user_data(self):
        print("******** reading flat file *********")

        global flatfile
        current_path = os.getcwd()
        flat_file = current_path + "\\user_file.txt"

        try:
            user_dict = {}
            with open(flat_file, 'r') as flatfile:
                for line in flatfile:
                    split_line = line.split()
                    user_dict[int(split_line[0])] = " ".join(split_line[1:])

        except IOError as err:
            errno, strerror = err.args
            print("I/O error({0}): {1}".format(errno, strerror))
        # finally:
        #    flat_file.close()

        # for keys, values in user_dict.items():
        #   print(keys)
        #    print(values)

        return user_dict

    def process_data(self):

        user_dict = self.read_user_data()

        global csvfile
        current_path = os.getcwd()
        csv_file = current_path + "\\exports\max-legacy\_007_max_partial4.csv"
        csv_columns = self.create_csv_headers()

        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_NONNUMERIC,
                                        lineterminator='\n')
                writer.writeheader()
                self.write_fields_to_csv_file(writer, self.response, user_dict)

        except IOError as err:
            errno, strerror = err.args
            print("I/O error({0}): {1}".format(errno, strerror))
        finally:
            csvfile.close()

        return

    @staticmethod
    def create_csv_headers():
        csv_columns = ['Category', 'Case', 'Title', 'Story Points', 'Priority',
                       'Assigned To', 'Tags', 'Fix Versions', 'Affect Versions', 'Area',
                       'Milestone', 'Date Opened', 'Project', 'Opened By', 'Salesforce Case', 'Due Date',
                       'HotFix', 'Resolved By', 'Original Estimate', 'Current Estimate',
                       'Date Resolved', 'Date Closed', 'Subcases', 'Status'
                       #,'QA Buddy',
                       ]
        return csv_columns

    def write_fields_to_csv_file(self, writer, response, user_dict):

        print("******** writing fields to csv file *********")

        #fb_dict = {}
        for case in response.cases.findAll('case'):
            assignees = case.find("events").findAll('ixPersonAssignedTo')
            events = case.find("events")
            comments = case.find("events").findAll('s')
            #event_date = case.find("events").findAll('dt')
            #event_person = case.find("events").findAll('ixPerson')
            #person = self.get_person(user_dict, int(event_person.string))

            self.fb_dict['Category'] = case.sCategory.string
            self.fb_dict['Case'] = case.ixBug.string
            self.fb_dict['Title'] = case.sTitle.string
            self.fb_dict['Story Points'] = case.dblStoryPts.string
            self.fb_dict['Priority'] = case.sPriority.string
            self.fb_dict['Status'] = case.sStatus.string
            self.fb_dict['Tags'] = case.tags.string
            self.fb_dict['Fix Versions'] = case.sFixFor.string
            #self.fb_dict['Fix Versions'] = "Salesforce Cases"
            #self.fb_dict['Affect Versions'] = case.sFixFor.string
            self.fb_dict['Area'] = case.sArea.string

            #self.fb_dict['Milestone'] = "012 : IT-Operations"
            self.fb_dict['Date Opened'] = self.format_date_field(case.dtOpened.string)
            self.fb_dict['Project'] = case.sProject.string
            #self.fb_dict['QA Buddy'] = self.get_person(user_dict,
            #                                      int(case.plugin_customfields_at_fogcreek_com_qaxbuddyf611.string))
            self.fb_dict['Opened By'] = self.get_person(user_dict, int(case.ixPersonOpenedBy.string))
            self.fb_dict['Salesforce Case'] = case.plugin_customfields_at_fogcreek_com_salesforcexcaseq17.string
            self.fb_dict['Due Date'] = self.format_date_field(case.dtDue.string)
            self.fb_dict['HotFix'] = case.plugin_customfields_at_fogcreek_com_hotfixp3b.string
            self.fb_dict['Resolved By'] = self.get_person(user_dict, int(case.ixPersonResolvedBy.string))
            self.fb_dict['Original Estimate'] = case.hrsOrigEst.string
            self.fb_dict['Current Estimate'] = case.hrsCurrEst.string
            self.fb_dict['Date Resolved'] = self.format_date_field(case.dtResolved.string)
            self.fb_dict['Date Closed'] = self.format_date_field(case.dtClosed.string)
            self.fb_dict['Subcases'] = self.split_comma_separated_list(case.ixBugChildren.string)
            self.fb_dict['Assigned To'] = self.get_last_assignee(user_dict, assignees)

            writer.writerow(self.fb_dict)
            self.fb_dict.clear()

    def format_date_field(self, date):
        if date:
            dtOpenedUtc = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            # dtFormatedUtc = dtOpenedUtc.strftime('%m/%d/%y %I:%M %p')
            #value = '{date:%m/%d/%y %I:%M %p}'.format(date=dtOpenedUtc)

            #datetimeField = (value[0:2] + "/" + value[3:5] + "/" + value[6:8] + " " + value[9:11] + ":" + value[12:14] + " " + value[15:17])
            #print(datetimeField)

            #value2 = time.strftime('%m/%d/%y %I:%M %p', time.strptime(date, '%Y-%m-%dT%H:%M:%SZ'))
            value2 = time.strftime('%m/%d/%y %I:%M %p', time.strptime(date, '%Y-%m-%dT%H:%M:%SZ'))

           # print(value2)

            return value2
        else:
            return ''

    def convert_to_decimal(self, x):
        try:
            # value = '{:.2f}'.format(round(x), 2)
            value = str(Decimal(x))
            return value

        except Exception as ex:
            return x

            # if this_variable % 1 == 0:
            #    return float(this_variable)
            # else:
            #    return this_variable

    def get_person(self, user_dict, key):

        try:
            value = user_dict[key]
            return value
        except KeyError:
            # Key is not present
            return

            # if key in user_dict:
            #    return user_dict[key]
            # else:
            #    return 'not found'

    def split_comma_separated_list(self, x):
        subcase_str = ""
        if x:
            subcases = x.split(',')
            for subcase in subcases:
                subcase_str += subcase + ','
            return subcase_str
        else:
            return x

    def get_last_assignee(self, user_dict, assignees):

        for assignee in reversed(assignees):
            value = int(assignee.text)
            if value and value > 1:
                break

        return self.get_person(user_dict, value)

    def get_event_history(self, events, comments):
        global letterVal
        count = 0
        #for comment in reversed(comments):
        #eventItr = iter(events)
        #eventItr.__next__
        #c = events.Children()
        #c.next()  # skip first item
        #letters = "a,b,c,d,f,g,h,i,j"
        #print()
        letter = "a"
        for event in events:
            comment = event.s
            event_date = event.dt.string
            event_user = event.sPerson.string
            dateValue = time.strftime('%m/%d/%Y %I:%M:%S', time.strptime(event_date, '%Y-%m-%dT%H:%M:%SZ'))
            #print(dateValue)
            if str(comment.text) != '' and str(comment.text) != str(comments[0].text):
                if count == 9:
                    count = 0
                    letter = chr(ord(letter) + 1)

                if letter == "g":
                    letter = "a"

                count = count + 1
                #letter = chr(ord(letter) + 1)
                #print(letter)
                value = str(count) + str(letter) + "_" + 'Comment'
                #"05/05/2010 11:20:30; adam; This is a comment."
                self.fb_dict[value] = '"' + dateValue + "; " + event_user + "; " + comment.text + '"'


    def get_comment_history(self, comments, event_date, person):

        count = 0
        #for comment in reversed(comments):
        for comment in comments:
            if comment:
                count = count + 1
                value = 'Comment' + str(count)
                #"05/05/2010 11:20:30; adam; This is a comment."
                self.fb_dict[value] = '"' + comment.text + '"'

                #''.join(comment.text) + '\n'

        #return fb_dict

        #comment_str = ''
        #for comment in reversed(comments):
        #    if comment:
        #        comment_str += ''.join(comment.text) + '\n'
        #        # end_string += '\n', '{0}'.format(''.join(comment.string))

        #return comment_str