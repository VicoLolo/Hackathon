import importlib
import os

from client.client import Client
from dal.service import DalService
from datalogger.logger_service import LoggerService
from rfq.rfq_sender import RfqService
from runner.allocator import AllocatorService
from runner.calendar import CalendarService
from runner.unwind import UnwindService


class Runner:
    # Runner must init services
    def __init__(self, year, withSocket):
        CalendarService()
        DalService()
        UnwindService()
        LoggerService(withSocket)
        RfqService()
        self.year = year
        CalendarService.set_start_year(year)
        self.clients = []
        AllocatorService(self.clients)
        self.working_days = DalService.get_working_days(year)

    def run(self):
        print(CalendarService.get_current_time())

        # import all the users from answers and add them all
        self.get_all_clients()

        self.run_year()

    def run_year(self):
        while CalendarService.get_current_time().year == self.year:
            while CalendarService.get_current_day_string() not in self.working_days:
                CalendarService.to_next_day()
            self.run_day()

    def run_day(self):
        CalendarService.set_begin_of_day()
        print(CalendarService.get_current_time())
        rfq_list = []

        for i in range(20):
            rfq_list.append(RfqService.generate_rfq())

        for rfq in rfq_list:
            print(rfq.get_sym(), rfq.get_qty())

            rfq_winner = AllocatorService.allocate_rfq(rfq)
            if rfq_winner is None:
                print('No Winner')
            else:
                print('Winner of the auction is ' + rfq_winner.get_name())
            print("\n")

        CalendarService.set_end_of_day()
        print(CalendarService.get_current_time())

        for client in self.clients:
            UnwindService.unwind_client(client)
            client.display_portfolio()

        CalendarService.set_next_business_day()
        print("\n\n------- NEW DAY -------")
        print(CalendarService.get_current_time())

    def get_all_clients(self):
        directory_answers = os.getcwd() + "/answers"
        for file in os.listdir(directory_answers):
            if file.endswith(".py"):
                filename = os.fsdecode(file)
                name = filename.split(".")[0]
                mod = importlib.import_module("answers." + name, __name__)
                client_new = Client(name, mod.answer_rfq)
                self.clients.append(client_new)