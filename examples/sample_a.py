# sample_a.py

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    if len(numbers) == 0:
        return 0
    return total / len(numbers)



def add(a: int, b: int) -> int:
    return a + b



class Processor:
    def process(self, data):
        for item in data:
            if item is None:
                continue
            print(item)

'''
Mile Stone 1: 
*Extract how many functions are defined in the code snippet.
*Extract how many classes are defined in the code snippet.
whats starting line of the function "add"?
does function contain any doc string or not?
coverage report
*from which line number to which line number is the function "calculate_average" defined?
*find the complexity of the function "calculate_average".
'''