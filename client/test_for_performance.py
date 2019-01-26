import threading
import time

from client import Client

class RunClientThread(threading.Thread):

    def __init__(self, thread_id, thread_name, delay_time, sents):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = thread_name
        self.delay_time = delay_time
        self.sents = sents

    def run(self):
        start_time = time.time()
        cli = Client(user_id=self.thread_id, host='39.105.100.46', port=80, session_id=None)
        end_time = time.time()
        new_sess_time_ms = 1000.0 * (end_time - start_time)
        
        time.sleep(self.delay_time)

        total_response_time_ms = 0.0
        for sent in self.sents:
            start_time = time.time()
            resp = cli.response(sent)
            end_time = time.time()
            total_response_time_ms += 1000.0 * (end_time - start_time)
            time.sleep(self.delay_time)

        print("Finished testing for %s, with requesting new session time `%.6f` ms, average responsing time `%.6f` ms" \
            % (self.name, new_sess_time_ms, total_response_time_ms / len(sents)))

if __name__ == "__main__":

    # 测试样例
    sents = ["你好", "5岁", "上过一年，但感觉没什么效果", "英语听说能力吧", \
        "没什么了解", "北京", "13126609255", "张日天", "爸爸", "天天"]
    
    # 模拟的线程个数
    num_threads = 1000

    # 平均作答时间（秒）
    average_delay = 0.1

    thread_list = []
    for i in range(num_threads):
        t = RunClientThread(i, "Thread-" + str(i + 1), average_delay, sents)
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()

    print("All test finished")
