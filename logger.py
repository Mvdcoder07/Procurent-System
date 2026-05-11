import pandas as pd
import time
from datetime import datetime
import config
import os

class EventLogger:
    def __init__(self, student_id):
        self.student_id = student_id
        self.events = []
        self.last_logged_event = None
        self.last_log_time = 0
        
        # Each student gets own log file
        self.log_file = config.get_student_log_file(student_id)
        print(f"Logger initialized for student: {student_id}")

    def log_event(self, event_type):
        current_time = time.time()

        if (event_type != self.last_logged_event or
            current_time - self.last_log_time > config.LOG_COOLDOWN):

            self.events.append({
                'student_id': self.student_id,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'event': event_type
            })

            self.last_logged_event = event_type
            self.last_log_time = current_time

            # Save to student specific file
            pd.DataFrame(self.events).to_csv(
                self.log_file, index=False)
            print(f"Event logged for {self.student_id}: {event_type}")

    def print_summary(self):
        print(f"\nSession Summary for {self.student_id}:")
        if self.events:
            df = pd.DataFrame(self.events)
            print(f"Total Events: {len(self.events)}")
            print(df['event'].value_counts().to_string())
        else:
            print("No suspicious events")