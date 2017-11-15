def backtracking_search(problem):
    return recursive_backtracking(problem, problem.initial_assignments,
    variable_algorithm = naive_variable, value_algorithm = naive_value)

def recursive_backtracking(problem, assignments, variable_algorithm, value_algorithm, gui):
    gui.update_gui(assignments)
    gui.root.update()
    if problem.check_solved(assignments):
        return assignments
    else:
        variable = variable_algorithm(problem, assignments)
        for valid_value in value_algorithm(problem, assignments, variable):
            new_assignments = assignments + [(variable, valid_value)]
            if not problem.check_assignment(new_assignments):
                continue
            result = recursive_backtracking(problem, new_assignments, variable_algorithm, value_algorithm, gui)
            if result is not None:
                return result
        # need a no solution value returned here

# assignments is list of pairs ((row,col), value)
def naive_variable(problem, assignments):
    return next(iter(problem.variables - {x[0] for x in assignments}))

def min_remaining_values(problem, assignments):
    min_len = None
    min_variable = None
    for variable in problem.variables - {x[0] for x in assignments}:
        n_values = len(naive_value(problem, assignments, variable))
        if min_len is None or n_values < min_len:
            min_len = n_values
            min_variable = variable

    return min_variable

def naive_value(problem, assignments, variable):
    domain = problem.domain.copy()
    row_cell, col_cell = map(lambda x: x // problem.sqrt_n, variable)
    for (row, col), value in assignments:
        if row == variable[0] or col == variable[1] or (row_cell == row // problem.sqrt_n and col_cell == col // problem.sqrt_n):
            domain.discard(value)
    return domain

def least_constraining_value(problem, assignments, variable):
    values = []
    for value in problem.domain:
        new_assignments = assignments + [(variable, value)]
        remaining_variables = problem.variables - {x[0] for x in new_assignments}
        new_len = sum([len(naive_value(problem, new_assignments, x)) for x in remaining_variables])
        values.append((value, new_len))
    values.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in values]
