import csv


def load_csv():
    with open("sales_data.csv",newline='') as rows:
        return list(csv.DictReader(rows))
          
def find_best_day(data):       
        result = max(data, key=lambda x: int(x["sales_amount"]))
        print (f"Best day: {result['date']} with {result['sales_amount']} UZS")

def find_worst_day(data):       
        result = min(data, key=lambda x: int(x["sales_amount"]))
        print (f"Worst day: {result['date']} with {result['sales_amount']} UZS")
    
def total_revenue(data):       
        result = sum(int(x["sales_amount"]) for x in data)
        print (f"Total revenue: {result} UZS")
        
def average_daily(data):       
        result = sum(int(x["sales_amount"]) for x in data) / len(data)
        print (f"Average daily: {result} UZS")
        
def most_popular_item(data):       
        items = {}
        for x in data:
            item = x["best_item"]
            if item in items:
                items[item] += 1
            else:
                items[item] = 1
        result = max(items, key=lambda x: items[x])
        print (f"Most popular item: {result} ({items[result]} orders)")

data = load_csv()

print("===Weekly Sales Report===")
find_best_day(data)
find_worst_day(data)
total_revenue(data)
average_daily(data)
most_popular_item(data)