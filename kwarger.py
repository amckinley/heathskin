class FooClass(object):
    def __init__(self, first_arg, *args, **kwargs):
        print "the first posititional arg is '{}'".format(first_arg)
        print "and the content of the kwargs is", kwargs
        print "and args is", list(args)

if __name__ == "__main__":
    f = FooClass("hey its mey arg", 42, 69, 128, 512, "butthole", balls_arg=False)
