#!/usr/bin/python
"""Created by jwk aug 2018"""
import main, getpass


class obsHelper(object):
    def __init__(self):
        self.getUserData()

    def getUserData(self):
        self.options = {}
        print(
            "Hello {0}, \n\tThis program helps plan observations with the White Telescope.\n".format(
                getpass.getuser()
            )
        )
        print(
            "You will need to make some choices about telescope configurations, this program "
            "will help make sure these choices are resononable, \nbut you will have to fine tune "
            "the values by trail and error to get exectly what you want.\n"
            "Be sure to report any questions or concerns to your instructors. "
            "If you get stuck, use ctrl c to close the program"
            "\n\tbest of luck,\n\tjwk\n"
        )

        while True:
            try:
                coordSys = raw_input(
                    "Would you like to point the telescope using [ALTAZ, RADEC]? "
                )
            except ValueError:
                print("Sorry, I can't parse your response.")
                continue

            if coordSys.upper() == "ALTAZ":
                self.options["coordSys"] = "AltAz"
                while True:
                    try:
                        alt = float(raw_input("Enter ALT [in decimal hours]: "))
                    except ValueError:
                        print("Sorry, I can't parse your response.")
                        continue
                    if alt <= 24.0 and alt >= 0.0:
                        self.options["alt"] = alt
                        break
                    else:
                        print("You entered a number out of range, lets try again")
                        continue
                    self.options["coordSys"] = "AltAz"

                while True:
                    try:
                        az = float(raw_input("Enter AZ [in decimal hours]: "))
                    except ValueError:
                        print("Sorry, I can't parse your response.")
                        continue
                    if az <= 90.0 and az >= 0.0:
                        self.options["az"] = az
                        break
                    else:
                        print("You entered a number out of range, lets try again")
                        continue

                break
            elif coordSys.upper() == "RADEC":
                self.options["coordSys"] = "RADEC"
                break
            else:
                print("You didn't enter a valid choice, lets try again")
                continue


if __name__ == "__main__":
    obsHelper()
