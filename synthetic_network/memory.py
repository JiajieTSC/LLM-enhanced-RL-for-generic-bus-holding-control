import random

class Memory:
    def __init__(self, size_max, size_min):
        self._samples_1 = []
        self._samples_2 = []
        self._samples_3 = []
        self._samples_4 = []
        self._samples_5 = []
        self._samples_6 = []
        self._samples_7 = []
        self._samples_8 = []
        self._samples_9 = []
        self._samples_10 = []
        self._size_max = size_max
        self._size_min = size_min


    def add_sample_1(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_1.append(sample)
        if self._size_now_1() > self._size_max:
            self._samples_1.pop(0)  # if the length is greater than the size of memory, remove the oldest element
    def add_sample_2(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_2.append(sample)
        if self._size_now_2() > self._size_max:
            self._samples_2.pop(0)
    def add_sample_3(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_3.append(sample)
        if self._size_now_3() > self._size_max:
            self._samples_3.pop(0)
    def add_sample_4(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_4.append(sample)
        if self._size_now_4() > self._size_max:
            self._samples_4.pop(0)
    def add_sample_5(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_5.append(sample)
        if self._size_now_5() > self._size_max:
            self._samples_5.pop(0)
    def add_sample_6(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_6.append(sample)
        if self._size_now_6() > self._size_max:
            self._samples_6.pop(0)  # if the length is greater than the size of memory, remove the oldest element
    def add_sample_7(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_7.append(sample)
        if self._size_now_7() > self._size_max:
            self._samples_7.pop(0)
    def add_sample_8(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_8.append(sample)
        if self._size_now_8() > self._size_max:
            self._samples_8.pop(0)
    def add_sample_9(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_9.append(sample)
        if self._size_now_9() > self._size_max:
            self._samples_9.pop(0)
    def add_sample_10(self, sample):
        """
        Add a sample into the memory
        """
        self._samples_10.append(sample)
        if self._size_now_10() > self._size_max:
            self._samples_10.pop(0)


    def get_samples_1(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_1() < self._size_min:
            return []

        if n > self._size_now_1():
            return random.sample(self._samples_1, self._size_now_1())  # get all the samples
        else:
            return random.sample(self._samples_1, n)  # get "batch size" number of samples
    def get_samples_2(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_2() < self._size_min:
            return []

        if n > self._size_now_2():
            return random.sample(self._samples_2, self._size_now_2())  # get all the samples
        else:
            return random.sample(self._samples_2, n)
    def get_samples_3(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_3() < self._size_min:
            return []

        if n > self._size_now_3():
            return random.sample(self._samples_3, self._size_now_3())  # get all the samples
        else:
            return random.sample(self._samples_3, n)
    def get_samples_4(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_4() < self._size_min:
            return []

        if n > self._size_now_4():
            return random.sample(self._samples_4, self._size_now_4())  # get all the samples
        else:
            return random.sample(self._samples_4, n)
    def get_samples_5(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_5() < self._size_min:
            return []

        if n > self._size_now_5():
            return random.sample(self._samples_5, self._size_now_5())  # get all the samples
        else:
            return random.sample(self._samples_5, n)  # get "batch size" number of samples
    def get_samples_6(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_6() < self._size_min:
            return []

        if n > self._size_now_6():
            return random.sample(self._samples_6, self._size_now_6())  # get all the samples
        else:
            return random.sample(self._samples_6, n)
    def get_samples_7(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_7() < self._size_min:
            return []

        if n > self._size_now_7():
            return random.sample(self._samples_7, self._size_now_7())  # get all the samples
        else:
            return random.sample(self._samples_7, n)
    def get_samples_8(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_8() < self._size_min:
            return []

        if n > self._size_now_8():
            return random.sample(self._samples_8, self._size_now_8())  # get all the samples
        else:
            return random.sample(self._samples_8, n)
    def get_samples_9(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_9() < self._size_min:
            return []

        if n > self._size_now_9():
            return random.sample(self._samples_9, self._size_now_9())  # get all the samples
        else:
            return random.sample(self._samples_9, n)  # get "batch size" number of samples
    def get_samples_10(self, n):
        """
        Get n samples randomly from the memory
        """
        if self._size_now_10() < self._size_min:
            return []

        if n > self._size_now_10():
            return random.sample(self._samples_10, self._size_now_10())  # get all the samples
        else:
            return random.sample(self._samples_10, n)
  


    def _size_now_1(self):
        """
        Check how full the memory is
        """
        return len(self._samples_1)
    def _size_now_2(self):
        """
        Check how full the memory is
        """
        return len(self._samples_2)
    def _size_now_3(self):
        """
        Check how full the memory is
        """
        return len(self._samples_3)
    def _size_now_4(self):
        """
        Check how full the memory is
        """
        return len(self._samples_4)
    def _size_now_5(self):
        """
        Check how full the memory is
        """
        return len(self._samples_5)
    def _size_now_6(self):
        """
        Check how full the memory is
        """
        return len(self._samples_6)
    def _size_now_7(self):
        """
        Check how full the memory is
        """
        return len(self._samples_7)
    def _size_now_8(self):
        """
        Check how full the memory is
        """
        return len(self._samples_8)
    def _size_now_9(self):
        """
        Check how full the memory is
        """
        return len(self._samples_9)
    def _size_now_10(self):
        """
        Check how full the memory is
        """
        return len(self._samples_10)