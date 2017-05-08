from utilities.jira_importer import JiraImporter

def call_utility():
    jira_import = JiraImporter()
    #.process_fogbugz_data()
    jira_import.create_versions()
    #jira_import.read_retry_data()

call_utility()
