import adafruit_ticks

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = adafruit_ticks.ticks_ms()
        result = f(*args, **kwargs)
        delta = adafruit_ticks.ticks_diff(adafruit_ticks.ticks_ms(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta))
        return result
    return new_func
