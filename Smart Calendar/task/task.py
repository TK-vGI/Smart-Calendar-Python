import re
from datetime import datetime


class DatetimeValidator:
    note_pattern: re.Pattern[str] = re.compile(r"""
        ^(?P<date>\d{4}-\d{1,2}-\d{1,2})  # Date part
        \s                                # Space
        (?P<hour>\d{2}):(?P<minute>\d{2}) # Time part
        $                                 # End
    """, re.VERBOSE)

    birthday_pattern: re.Pattern[str] = re.compile(r"""
        ^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$
    """, re.VERBOSE)

    @classmethod
    def matches(cls, input_str: str, pattern: re.Pattern[str]) -> bool:
        return bool(pattern.match(input_str))

    @classmethod
    def is_valid_note_datetime(cls, input_str: str) -> bool:
        if not cls.matches(input_str, cls.note_pattern):
            return False
        try:
            date_part, time_part = input_str.split(" ")
            year, month, day = map(int, date_part.split("-"))
            hour, minute = map(int, time_part.split(":"))

            if not (1 <= month <= 12 and 0 <= hour < 24 and 0 <= minute < 60):
                return False

            datetime(year, month, day, hour, minute)
            return True
        except (ValueError, IndexError):
            return False

    @classmethod
    def is_valid_birthday(cls, input_str: str) -> bool:
        if not cls.matches(input_str, cls.birthday_pattern):
            return False
        try:
            year, month, day = map(int, input_str.split("-"))

            if not (1 <= month <= 12):
                return False

            datetime(year, month, day)  # Catches invalid day/month combos
            return True
        except ValueError:
            return False


class SmartCalendar:
    def __init__(self):
        self.tasks = []

    def get_current_datetime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def notes_time_remaining(self, input_dt):
        try:
            current_dt = datetime.now()
            target_dt = datetime.strptime(input_dt, "%Y-%m-%d %H:%M")
            time_diff = target_dt - current_dt
            if time_diff.total_seconds() < 0:
                return "Time is in the past", 0
            days = time_diff.days
            hours = time_diff.seconds // 3600
            remainder = time_diff.seconds % 3600
            minutes = 1 + (remainder // 60)
            if minutes == 60:
                hours = hours + 1
                minutes = 0
            if hours == 24:
                days = days + 1
                hours = 0
            parts = [f"{days} day(s)", f"{hours} hour(s)", f"{minutes} minute(s)"]
            return ", ".join(parts), 0
        except ValueError:
            return "Invalid datetime format", 0

    def birthdays_time_remaining(self, input_dt):
        try:
            current_dt_ = datetime.strftime(datetime.now(), "%Y-%m-%d")
            current_dt = datetime.strptime(current_dt_, "%Y-%m-%d")
            target_date = datetime.strptime(input_dt, "%Y-%m-%d")
            current_year = current_dt.year
            next_birthday = datetime(current_year, target_date.month, target_date.day)
            if next_birthday <= current_dt:
                next_birthday = datetime(current_year + 1, target_date.month, target_date.day)
            time_diff = next_birthday - current_dt
            days = time_diff.days
            years = current_year - target_date.year
            if next_birthday.year == current_year + 1:
                years += 1
            if days < 0:
                return "Time is in the past", 0
            return f"{days} day(s)", years
        except ValueError:
            return "Invalid datetime format", 0

    def add_note(self):
        """
        Prompts the user to add one or more new note-type tasks.

        Workflow:
        - Asks for the number of notes to create.
        - For each note:
            - Validates the input datetime format ("YYYY-MM-DD HH:MM").
            - Checks logical validity of date and time values.
            - Requests a text description for the note.
            - Calculates time remaining until the note's datetime.
            - Adds the note to the calendar if valid.
        - After all notes are added, displays only the newly added notes.

        Notes:
        - Validation is performed using the DatetimeValidator class.
        - Display format includes task text and remaining time.
        """

        new_notes = []  # Temp list for storing newly added notes.

        while True:
            try:
                note_num = int(input("How many notes would you like to add: ").strip())
                if note_num <= 0:
                    print("Incorrect number")  # Incorrect number of notifications
                else:
                    break
            except ValueError:
                print("Incorrect number")  # Incorrect number of notifications

        for i in range(1, note_num + 1):
            while True:
                input_dt = input(f"{i}. Enter datetime in \"YYYY-MM-DD HH:MM\" format:").strip()
                # Checks for incorrect format, can't be parsed in YYYY-MM-DD HH:MM
                if DatetimeValidator.matches(input_dt, DatetimeValidator.note_pattern):
                    # Checks for wrong date/time values
                    if DatetimeValidator.is_valid_note_datetime(input_dt):
                        input_txt = input("Enter text:").strip()
                        remaining_time, dump = self.notes_time_remaining(input_dt)
                        if remaining_time not in ["Invalid datetime format", "Time is in the past"]:
                            new_note = {
                                "type": "note",
                                "datetime": input_dt,
                                "text": input_txt,
                                "remaining": remaining_time,
                                "years": 0
                            }
                            self.tasks.append(new_note)
                            new_notes.append(new_note)
                            break
                        else:
                            print(remaining_time)
                        break
                    else:
                        print("Incorrect date or time values")
                else:
                    print("Incorrect format")

        # Output only newly added notes
        for task in new_notes:
            print(f'Note: "{task["text"]}" Remains: {task["remaining"]}')

    def add_birthday(self):
        """
        Prompts the user to add one or more new birthday-type tasks.

        Workflow:
        - Asks for the number of birthdays to create.
        - For each birthday:
            - Validates the input date format ("YYYY-MM-DD").
            - Checks logical validity of the birthdate.
            - Requests a name associated with the birthday.
            - Calculates the number of days until the next birthday and the upcoming age.
            - Adds the birthday to the calendar if valid.
        - After all birthdays are added, displays only the newly added birthdays.

        Notes:
        - Validation is performed using the DatetimeValidator class.
        - Display format includes the name, age to be reached, and time remaining.
        """

        new_birthdays = []  # Temp list for storing newly added birthdays.

        while True:
            try:
                birth_num = int(input("How many dates of birth would you like to add: ").strip())
                if birth_num <= 0:
                    print("Incorrect number")  # Incorrect number of notifications
                else:
                    break
            except ValueError:
                print("Incorrect number")  # Incorrect number of notifications

        for i in range(1, birth_num + 1):
            while True:
                input_dt = input(f"{i}. Enter date of birth in \"YYYY-MM-DD\" format: ").strip()
                # Checks for incorrect format, can't be parsed in YYYY-MM-DD
                if DatetimeValidator.matches(input_dt, DatetimeValidator.birthday_pattern):
                    # Checks for wrong date values
                    if DatetimeValidator.is_valid_birthday(input_dt):
                        input_txt = input("Enter name:").strip()
                        remaining_time, years = self.birthdays_time_remaining(input_dt)
                        if remaining_time not in ["Invalid datetime format", "Time is in the past"]:
                            new_birthday = {
                                "type": "birthday",
                                "datetime": input_dt,
                                "text": input_txt,
                                "remaining": remaining_time,
                                "years": years
                            }
                            self.tasks.append(new_birthday)
                            new_birthdays.append(new_birthday)
                            break
                        else:
                            print(remaining_time)
                        break
                    else:
                        print("Incorrect date or time values")
                else:
                    print("Incorrect format")

        # Output only newly added notes
        for task in new_birthdays:
            print(f'Birthday: "{task["text"]} (turns {task["years"]})" - {task["remaining"]}')

    def output_tasks(self, filter: str = "all") -> None:
        # if not self.tasks:
        #     print("No tasks to display")
        #     return

        filtered_tasks = []

        if filter == "all":
            filtered_tasks = self.tasks
        elif filter == "text":
            text = input("Enter text: ").strip()
            filtered_tasks = [t for t in self.tasks if text.lower() in t.get("text", "").lower()]
        elif filter == "date":
            while True:
                date_str = input("Enter date in \"YYYY-MM-DD\" format: ").strip()
                if DatetimeValidator.is_valid_birthday(date_str):
                    date_input = datetime.strptime(date_str, "%Y-%m-%d")
                    if datetime.now().year <= date_input.year:
                        filtered_tasks = [
                            t for t in self.tasks
                            if datetime.strptime(t["datetime"].split(" ")[0], "%Y-%m-%d").month == date_input.month
                               and datetime.strptime(t["datetime"].split(" ")[0], "%Y-%m-%d").day == date_input.day
                        ]
                    else:
                        filtered_tasks = [
                            t for t in self.tasks
                            if t["type"] == "birthday"
                               and datetime.strptime(t["datetime"].split(" ")[0], "%Y-%m-%d").month == date_input.month
                               and datetime.strptime(t["datetime"].split(" ")[0], "%Y-%m-%d").day == date_input.day
                        ]
                    break
                else:
                    print("Incorrect date or time values")

        else:  # filter is "note" or "birthday"
            filtered_tasks = [t for t in self.tasks if t["type"] == filter]

        # Output the filtered tasks
        filtered_tasks.sort(key=lambda t: t["type"])
        for task in filtered_tasks:
            if task["type"] == "note":
                print(f'Note: "{task["text"]}" Remains: {task["remaining"]}')
            elif task["type"] == "birthday":
                print(f'Birthday: "{task["text"]} (turns {task["years"]})" - {task["remaining"]}')

    def view_tasks(self):
        task_type_aliases = {
            "all": "all",
            "date": "date",
            "text": "text",
            "birthdays": "birthday",
            "notes": "note"
        }
        while True:
            user_filter = input("Specify filter (all, date, text, birthdays, notes): ")
            if user_filter in task_type_aliases:
                break
            else:
                print("Incorrect type")

        normalized_filter = task_type_aliases[user_filter]
        self.output_tasks(filter=normalized_filter)

    def delete_task(self):
        print("Not implemented yet")

    def run(self):
        print("Current date and time:")
        print(self.get_current_datetime())
        while True:
            command = input("Enter the command (add, view, delete, exit): ").strip().lower()
            if command == "add":
                note_type = input("Specify type (note, birthday):").strip().lower()
                if note_type == "note":
                    self.add_note()
                elif note_type == "birthday":
                    self.add_birthday()
                else:
                    print("Incorrect type")  # Incorrect type of notification
            elif command == "view":
                self.view_tasks()
            elif command == "delete":
                self.delete_task()
            elif command == "exit":
                print("Goodbye!")
                exit(0)
            else:
                print("Incorrect command")  # Incorrect menu command


if __name__ == "__main__":
    SmartCalendar().run()
