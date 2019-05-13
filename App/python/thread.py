import threading

def say_hello(count, name):
    print("Hello world!", name)
    count -= 1
    print(count)

def main():
    name_list = ['Bob', 'Jack', 'Jone', 'Mike', 'David']
    for i in range(5):
        thread = threading.Thread(target=say_hello, args=(10, name_list[i]))
        thread.start()

main()