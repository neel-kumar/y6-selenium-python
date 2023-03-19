import re
import time
import random
import logging
import winsound
import pandas as pd


def beep(frequency=500, duration=200):
    # frequency = 500  # Set Frequency To 500 Hertz
    # duration = 200  # Set Duration To 200 ms
    winsound.Beep(frequency, duration)


def rsleep_within(low, high):
    millis = random.randint(low, high)
    logging.debug(f"Sleeping for {millis} milliseconds.")
    time.sleep(millis/1000)


def rsleep():
    rsleep_within(100, 500)


def rsleep_long():
    rsleep_within(500, 1000)


def config_logging():
    logging.basicConfig(format='%(levelname)s: %(asctime)s - %(message)s', level=logging.INFO)


def read_members_xlsx(xlsx):
    df = pd.read_excel(xlsx)
    labels = df.iloc[3:4].values.flatten().tolist()
    return df.iloc[4:].set_axis(labels, axis=1).reset_index()


class Utils:

    def get_typ(text):
        match = re.search("(.*) - call/Text", text)
        if not match:
            match = re.search("(.*) call/Text", text)

        if match:
            return match.group(1)

        return None

    def get_typ_old(text):
        typ = text.find(" -")
        if typ == -1:
            typ = text.find(" call/Text")
        
        if typ != -1:
            return text[0:typ]
        else:
            return None


    def get_cellno(text):
        match = re.search("call/Text (to rebook )?(.*) \(cell\)", text)
        if match:
            return match.group(2)

        return None


    def get_prospect_details(text):
        typ = Utils.get_typ(text)
        cell = Utils.get_cellno(text)
        if typ and cell:
            return (typ, cell)
        else:
            return None


if __name__ == '__main__':
    for v in ["Same Day call/Text 4085824140 (cell)",
              "New Unscheduled Day 3 - call/Text 4084106107 (cell)",
              "New Unscheduled Day 3 - call/Text 4084256967 (celll)",
              "New Unscheduled Day 3 - call/Text 4085611861 (cell) 408561186 (home)",
              "New Unscheduled Day 7 - call/Text 5105522155 (cell) 510 (home)",
              "New Unscheduled Day 7 - call/Text 4084897182 (cell)",
              "New Unscheduled Day 7 - call/Text 8327593335 (cel) 8327593336 (home)",
              "New Unscheduled Day 7 - call/Text 4086502856 (cell) 4086502857 (home)",
              "Missed Sale Day 30 - call/Text (408) 800-9395 (cell) (408) 800-9395 (home)",
              "Missed Sale Day 7 - call/Text +13193614155 (cell)",
              "Missed Sale - Day 1 call/Text 203-733-5586 (cell)",
              "Missed Sale - Day 1 call/Text 4086618461 (cell)",
              "Day Prior Booking Confirmation - call/Text 6177946237 (cell) 6177946237 (home)",
              "Missed Sale - Day 1 call/Text 203-733-5586 (cell)",
              "Same Day call/Text 4083947464 (cell) 4083947464 (home)",
              "Renewed Interest - Day 3 - call/Text 4085837226 (cell) 4085837225 (home)",
              "Cancelled Booking - call/Text to rebook 6177946237 (cell) 6177946237 (home)",
              "Cancelled Booking Day 3 - call/Text 6177946237 (cell) 6177946237 (home)",
              "Cancelled Booking - call/Text to rebook 4086231304 (cell) 4086231304 (home)",
              "1st Class for $10 NOT BOOKED - Day 3 - call/Text to Book (313) 828-3020 (cell)",
              "10 pack - 3 session left - Check In",
              "Mobile Free Class - Unscheduled - Day 3 call 4056483715 (cell)",
              "call (224) 567-0716 (cell)",
              ]:
        print(f"Text: {v} detail :{Utils.get_prospect_details(v)}:")
