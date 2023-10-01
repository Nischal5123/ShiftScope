import csv

class bufferWriter:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.header = ["STATE", "ACTION", "REWARD"]
        self.data = []

    def add_state(self, state):
        self.current_entry = [state]

    def add_action(self, action):
        if hasattr(self, 'current_entry'):
            self.current_entry.append(action)
        else:
            self.current_entry = [None, action]

    def add_reward(self, reward):
        if hasattr(self, 'current_entry'):
            self.current_entry.append(reward)
            self.data.append(self.current_entry)
            delattr(self, 'current_entry')

    def write_to_csv(self):
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.header)
            writer.writerows(self.data)
        print(f'Data has been written to {self.csv_file_path}')



if __name__ == '__main__':
    # Example usage:

    # Create an instance of the CSVWriter class
    csv_writer = bufferWriter('output.csv')

    # Add state, action, and reward separately
    csv_writer.add_state("State 1")

    csv_writer.add_action("Action 1")
    csv_writer.add_state("State 2")
    # Some other function can add reward when it's available
    # For example, in another function:
    reward = 10
    csv_writer.add_reward(reward)

    # Write the data to the CSV file
    csv_writer.write_to_csv()
