import logging
import datetime

from decimal import Decimal

from prickle.forms.timesheet import TimesheetForm

from pylons import request, response, session, tmpl_context as c, url
from pylons.decorators import validate
from pylons.controllers.util import abort, redirect

from prickle.lib.base import BaseController, render

from prickle.model.timesheet import Timesheet, Project


log = logging.getLogger(__name__)

class TimesheetController(BaseController):
    def index(self):
        today = datetime.date.today()
        c.title = "Log Time"
        c.entry_title = "This Month's Entries"
        c.timesheets = Timesheet.for_month(today.year, today.strftime("%m"))
        c.timesheets = Timesheet.all_timesheets()
        c.project_list = Project.project_list()
        c.date = datetime.date.today()
        return render('/timeform.html')

    @validate(schema=TimesheetForm, form='index')
    def logit(self):
        timesheet = Timesheet(
                date=self.form_result['date'],
                duration=self.form_result['duration'],
                project=self.form_result['project'],
                description=self.form_result['description'])
        timesheet.store()
        return redirect(url(controller="timesheet", action="index"))

    def date(self, date):
        c.title = "Log Time for %s" % date
        c.entry_title = "Timesheets for %s" % date
        c.timesheets = Timesheet.for_date(date)
        # Would it be optimal to do this inside couchdb using a reduce function?
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        c.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        c.project_list = Project.project_list()
        return render('/timeform.html')

    def month(self, year, month):
        c.title = "Timesheet summary for %s" % month, year
        c.timesheets = Timesheet.for_month(year, month)
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        return render('/timesheet_summary.html')
    
    def project(self, id):
        c.project = Project.load_or_create(id)
        c.timesheets = Timesheet.for_project(id)
        c.title = "Timesheets for %s" % id
        c.total_time = sum(t.duration for t in c.timesheets)
        c.total_fee = sum(t.fee for t in c.timesheets)
        return render('/project_summary.html')
