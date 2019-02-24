import pandas as pd

data = pd.read_csv("data.csv")

productIds = data.columns[1:]
newData = []

for index, row in data.iterrows():
    lst = list(row)
    userId = lst[0]
    ratings = lst[1:]
    for i in range(len(productIds)):
        newData.append([userId, productIds[i], ratings[i]])

exportData = pd.DataFrame(newData, columns = ["userId", "productId", "rating"])

exportData.to_csv('ratings.csv', encoding='utf-8', index=False)