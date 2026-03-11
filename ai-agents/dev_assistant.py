from error_agent import ErrorAgent

error_agent = ErrorAgent()

def handle_system_error(error):
    return error_agent.handle_error(str(error))

def log_solution(problem, solution):
    from dev_memory import DevMemory
    memory = DevMemory()
    memory.log_problem(problem, solution)

