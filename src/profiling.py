import time

function_total_time = {}
function_calls = {}
start = time.perf_counter()


def benchmark(func):
    def wrapper(*args, **kwargs):
        if func.__name__ in function_calls.keys():
            function_calls[func.__name__] += 1
        else: function_calls[func.__name__] = 1
        t = time.perf_counter()
        res = func(*args, **kwargs)
        dt = time.perf_counter()-t
        if func.__name__ in function_total_time.keys():
            function_total_time[func.__name__] += dt
        else: function_total_time[func.__name__] = dt
        return res
    return wrapper


def profile():
    stop = time.perf_counter()
    screen_length = 120
    file_text = "\n"
    title = "Profiling"
    title_line = ('=' * (screen_length // 2 - len(title))
                  + title
                  + '='*(screen_length//2-len(title)))
    file_text += title_line+"\n"
    line = ("Function"
            + ' ' * ((screen_length // 5) - len("Function"))
            + ' '*((screen_length//5 - 1) // 2)
            + "Calls"
            + ' '*((screen_length//10) - len("Calls"))
            + ' '*((screen_length//5 - 1) // 2)
            + "Time %"
            + ' '*((screen_length//10) - len("Time %"))
            + ' '*((screen_length//5 - 1) // 2)
            + "Total"
            + ' '*((screen_length//10) - len("Total"))
            + ' '*((screen_length//5 - 1) // 2)
            + "Moy"
            + ' '*((screen_length//10) - len("Moy")))
    print(title_line)
    print(line)
    file_text += line+"\n"
    for function in function_calls:
        moy = str(function_total_time[function]/function_calls[function])
        calls = str(function_calls[function])
        perc = str(function_total_time[function]/(stop-start)*100)[:4]
        tot = str(function_total_time[function])[:10]
        line = (function
                + ' ' * ((screen_length//5) - len(function))
                + ' '*((screen_length//5 - 1) // 2)
                + calls
                + ' '*((screen_length//10) - len(calls))
                + ' '*((screen_length//5 - 1) // 2)
                + perc
                + ' '*((screen_length//10) - len(perc))
                + ' '*((screen_length//5 - 1) // 2)
                + tot
                + ' '*((screen_length//10) - len(tot))
                + ' '*((screen_length//5 - 1) // 2)
                + moy
                + ' '*((screen_length//10) - len(moy)))
        print(line, end="\n")
        file_text += line + "\n"
    try:
        open("profiling.txt", 'r')
    except FileNotFoundError:
        open("profiling.txt", 'w').close()
    with open("profiling.txt", 'a') as file:
        file.write(file_text)
