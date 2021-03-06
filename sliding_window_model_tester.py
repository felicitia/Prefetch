import time
import math

class SlidingWindowModelTester:
    urls = []

    def __init__(self, window_size, model_build_func, history_count=1):
        """
        Sliding Window Prefetching
        :param window_size:   (“URL size” = 50, 100, 200, 300, 400, 500)
        :param model_build_func: a function that builds a model without arguments.
        :param history_count: how many urls used for predict engine .It's 1 for DG.
        """
        self.window_size = window_size
        self.model_build_func = model_build_func

        self.history_count = history_count

    def load_urls(self, urls):
        """
        load urls
        :param urls:
        :return:
        """
        self.urls = urls

    def train_and_test(self, train_ratio=0.8):
        total_urls = len(self.urls)
        cache_set = set()
        hit_set = set()
        miss_set = set()
        hit_count = 0
        miss_count = 0
        prefetch_count = 0

        begin = math.ceil(self.window_size * train_ratio)

        end = self.window_size - 1
        t0 = time.time()
       
        while end < total_urls:
            # print(begin,end,begin-math.ceil(self.window_size * train_ratio))
            model = self.model_build_func()
            for url in self.urls[begin-math.ceil(self.window_size * train_ratio):begin]:
                model.feed(url)

            while begin < end:
                # predict engine
               
                current_url = self.urls[begin]
                
                # print(self.urls[begin - self.history_count:begin][0] ==self.urls[begin - 1] )
                # " history count == 1 " "
                predict_urls = model.predict(self.urls[begin - self.history_count:begin])
                # print(current_url in self.urls[begin - self.history_count:begin],current_url in predict_urls)
                for predict_url in predict_urls:
                    if predict_url not in cache_set:
                        cache_set.add(predict_url)
                        prefetch_count += 1


                if current_url in cache_set:
                    hit_set.add(current_url)
                    hit_count += 1
                else:
                    # add miss set
                    miss_set.add(current_url)
                    miss_count += 1
                
                 # continuous training
                model.feed(current_url)

                begin += 1

            precision = len(hit_set) / (len(cache_set) or 1)
            recall = (hit_count / (miss_count + hit_count)) if (miss_count + hit_count) else 0
            # print("p",precision,len(hit_set),len(cache_set) )
            # print("r",recall,hit_count+miss_count)
            # yield stage result
            # print(cache_set)
            # print(hit_set)
            yield len(cache_set), len(hit_set), len(
                miss_set), hit_count, miss_count, prefetch_count, precision, recall, time.time() - t0

            # sliding
    
            end += math.ceil(self.window_size * (1-train_ratio))

            # should I clear all set here ? -- Yes
            cache_set.clear()
            hit_set.clear()
            miss_set.clear()
            hit_count = 0
            miss_count = 0
            prefetch_count = 0

        return False
