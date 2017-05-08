from fogbugz_export import FogbugzExport


def call_utility():
    fb_export = FogbugzExport()
    fb_export.process_data()
    #fb_export.get_milestones_by_project_id()

call_utility()
