from client.position import Position
from dal.service import DalService
from runner.calendar import CalendarService


class AllocatorService:
    class __Allocator:
        def __init__(self, clients):
            self._clients = clients

        # noinspection PyBroadException
        def allocate_rfq(self, incoming_rfq):
            winning_client = None
            best_bet = None
            rfq_as_pos = Position(incoming_rfq.get_sym(), incoming_rfq.get_qty(), CalendarService.get_current_time())
            if incoming_rfq.get_qty() > 0:
                best_bet = 0
                for client in self._clients:
                    try:
                        client_ans = client.answer_rfq(incoming_rfq)
                    except:
                        client_ans = None
                    print(str(client.get_name()) + ' answer is ' + str(client_ans))
                    if client_ans is not None and client_ans > best_bet:
                        winning_client = client
                        best_bet = client_ans
            if incoming_rfq.get_qty() <= 0:
                best_bet = 1000000
                for client in self._clients:
                    try:
                        client_ans = client.answer_rfq(incoming_rfq)
                    except:
                        client_ans = None
                    print(str(client.get_name()) + ' answer is ' + str(client_ans))
                    if client_ans is not None and client_ans < best_bet:
                        winning_client = client
                        best_bet = client_ans

            if winning_client is not None:
                winning_client.add_to_portfolio(rfq_as_pos)
                # why do we already adjust pnl against the market price, it's not like we are hedging each position
                winning_client.adjust_pnl(incoming_rfq.get_qty() * (
                        DalService.get_price_stock(incoming_rfq.get_sym(),
                                                   CalendarService.get_current_time()) - best_bet))
                return winning_client
            return None

    instance = None

    def __init__(self, clients):
        if not AllocatorService.instance:
            AllocatorService.instance = AllocatorService.__Allocator(clients)

    @staticmethod
    def allocate_rfq(incoming_rfq):
        return AllocatorService.instance.allocate_rfq(incoming_rfq)
