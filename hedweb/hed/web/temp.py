import json

if __name__ == '__main__':
    print("hello world")
    with open('./static/resources/services.json') as f:
        dict = json.load(f)
    print(dict)