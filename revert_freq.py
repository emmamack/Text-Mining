""" Creates a graphic to represent the reverted edits per year of certain Wikipedia articles.
Wik_edits_pg class: also has capabilities to compute fraction of edits that are reverts.
Author: Emma Mack
"""

import re
from bs4 import BeautifulSoup as bs
import requests
import datetime
import matplotlib.pyplot as plt
import pickle

class Wik_edits_pg:
    def __init__(self, title):
        self.title = title

    def html(self, first_date = ""):
        link =  "https://en.wikipedia.org/w/index.php?title=" + self.title + "&offset=" + first_date + "&limit=500&action=history"
        return bs(requests.get(link).text, 'lxml')

    def text(self,first_date = ""):
        html = self.html(first_date)
        return html.get_text()

    def frac_reverts(self):
        text = self.text()
        num_reverts = len(re.findall("Reverted",text))
        return num_reverts/500

    def last_date_on_pg(self, edits_text):
        last_cur_index = edits_text.rfind("prev")
        date_first_index = last_cur_index + 13
        #assuming edits are in the 2000s. This will also break in 2020
        date_last_index = edits_text.rfind("20",date_first_index,date_first_index + 15) + 4
        last_date =  edits_text[date_first_index:date_last_index]
        words = last_date.split()
        months = ["0th entry","January","February","March","April","May","June","July",
                    "August","September","October","November","December"]
        return int(words[2]), months.index(words[1]), int(words[0])

    def reverts_per_yr(self):

        text = self.text()
        lyr, lmonth, lday = self.last_date_on_pg(text)
        now = str(datetime.datetime.now())
        nyr, nmonth, nday = int(now[0:4]), int(now[5:7]), int(now[8:10])
        total_days = 365*(nyr-lyr) + 30.5*(nmonth-lmonth) + (nday-lday)

        num_reverts = len(re.findall("Reverted",text))
        return 365*(num_reverts/total_days)


def reverts_group(*name_lists):
    per_yr_data = []
    frac_reverts_data = []
    labels = []
    for name_list in name_lists:
        for name in name_list:
            pg =  Wik_edits_pg(name)
            per_yr_data.append(pg.reverts_per_yr())
            frac_reverts_data.append(pg.frac_reverts())
        labels.extend(name_list)
        labels.append("")
        per_yr_data.append(0)
        frac_reverts_data.append(0)
    del per_yr_data[-1]
    del frac_reverts_data[-1]
    return (per_yr_data, frac_reverts_data, labels)

def reverts_per_yr_graphic(data, labels):
    y_pos = [3*x for x in list(range(len(data)))]
    plt.bar(y_pos, data)
    plt.xticks(y_pos,labels, rotation = "vertical")
    plt.ylabel('Reverts Per Year')
    plt.title('Reverts Per Year of Contentious vs. Non-contentious Wikipeida Articles')
    plt.savefig("Reverts_per_Year")
    plt.show()

def frac_reverts_graphic(data, labels):
    y_pos = [4*x for x in list(range(len(data)))]
    plt.bar(y_pos, data)
    plt.xticks(y_pos,labels, rotation = "vertical")
    plt.ylabel('Fraction of Edits that are Reverts')
    plt.title('Fraction of Edits of Wikipeida Articles that are Reverts')
    plt.savefig("Frac_Reverts")
    plt.show()

if __name__ == '__main__':
    contentious = ["Donald Trump", "Marine Le Pen", "Colin Powell", "Kim Jong Un"]
    non_contentious = ["Oprah Winfrey", "Matt Smith", "Justin Bieber", "Harry Styles"]
    data1, data2, labels = reverts_group(contentious, non_contentious)
    reverts_per_yr_graphic(data1, labels)
    frac_reverts_graphic(data2, labels)
