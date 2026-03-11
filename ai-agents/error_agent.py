from dev_memory import DevMemory

class ErrorAgent:

    def __init__(self):
        self.memory = DevMemory()

    def handle_error(self, error_message):

        matches = self.memory.search(error_message)

        if matches:
            print("Known issue found:")
            print(matches[0])
            return matches[0]

        print("Unknown problem. Logging.")
        self.memory.log_problem(error_message, "Pending solution")

        return None
