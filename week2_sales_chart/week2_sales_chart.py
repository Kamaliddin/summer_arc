import matplotlib.pyplot as plt
import statistics
import csv
def load_csv():
    with open('sales_data.csv', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader)

data = load_csv()

dates = [row["date"] for row in data]
amounts = [int(row["sales_amount"]) for row in data]

print("Dates:", dates)
print("Sales Amounts:", amounts)

average = statistics.mean(amounts)
colors = ['green' if amount >= average else 'red' for amount in amounts]
plt.figure(figsize=(10, 10))
plt.bar(dates, amounts, color=colors)
plt.title('Daily Sales Amount')
plt.axhline(average, color='blue', linestyle='--', label=f'Average: {average:.2f} UZS')
plt.legend()
plt.ylabel('Sales Amount (UZS)')
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sales_chart.png')