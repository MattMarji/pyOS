import Queue

class Task (object):

    taskid = 0

    def __init__(self, target):
        # Target is a function. Does something.

        self.tid = Task.taskid + 1
        self.target = target
        self.sendVal = None

    def run(self):
        return self.target.send(self.sendVal)

class Scheduler (object):
    def __init__(self):
        self.ready = [] # Assume queue class already implemented
        self.taskmap = {} # Map TaskID/PID to task object

    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def schedule(self, task):
        self.ready.insert(0,task) # FIFO - put in queue

    def exit(self, task):
        print "Task %d terminated" % task.tid
        del self.taskmap[task.tid]

    def mainloop(self):
        while self.taskmap:
            task = self.ready.pop() # Get task from queue
            try:
                result = task.run() # Resume coroutine

                if isinstance(result, SystemCall):
                    result.task = task
                    result.schedule = self
                    result.handle()
                    continue

            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)

class SystemCall (object):
    def handle(self):
        pass

class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.schedule.schedule(self.task)

class NewTask(SystemCall):
    def __init__(self, target):
        self.target = target

    def handle(self):
        tid = self.schedule.new(self.target)
        self.task.sendval = tid
        self.schedule.schedule(self.task)

class KillTask(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        task = self.schedule.taskmap.get(self.tid, None)

        if task:
            task.target.close()
            self.task.sendval = True

        else:
            self.task.sendval = False

        self.schedule.schedule(self.task)

def sometask():
    t1 = yield NewTask(foo())

def foo():
    mytid = yield GetTid()
    while True:
        print "I'm foo", mytid
        yield

def bar():
    mytid = yield GetTid()
    while True:
        print "I'm bar", mytid
        yield

scheduler = Scheduler()
scheduler.new(foo())
scheduler.new(bar())
scheduler.mainloop()
