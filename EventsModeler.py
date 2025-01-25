import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime

class Attendee:

    def __init__(self, name: str, date: datetime, org: str, member: bool, sales: int, attended: int):
        pass

    def get_name(self) -> str:
        return self.name

    def get_date(self) -> datetime:
        return self.date
    
    def get_org(self) -> str:
        return self.org

    def get_member(self) -> bool:
        return self.member
    
    def get_sales(self) -> int:
        return self.sales
    
    def get_attended(self) -> int:
        return self.attended



class EventsModeler:

    def __init__(self):
        pass

    def model(self, q: str) -> None:

        f = pd.read_excel("C:\\Users\\adria\\Downloads\\DeisHacks (Responses).xlsx")
        df = pd.DataFrame(f)
        
        mems = 0
        nons = 0

        if q == "Are you a member of Waltham Chamber of Commerce":
            for e in df["Are you a member of Waltham Chamber of Commerce"]:
                if str(e) == "Member":
                    mems += 1
                if str(e) == "Non-member":
                    nons += 1
        
        c = [mems, nons]
        labels = ["Members", "Non-members"]
        
        plt.pie(c, labels = labels)
        plt.title("Pie Chart Members vs Non-members")
        plt.show()


'''
0 - indexes/date/timestamp
1 - emails
2 - company
3 - member status
4 - yearly sales (paid or not paid)
5 - attended y/n
6 - date
7 - how long been member
8 - fundraiser/vendor
9 - satisification w wcc
10 - reasons for nonmembership
11 - likeliness to become a member
12 - industry
13 - comments
14 - size of the business
15 - preferred communication

'''


x = EventsModeler()
x.model("Are you a member of Waltham Chamber of Commerce")
