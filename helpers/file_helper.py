import pandas as pd

def to_csv(data: list):
    df = pd.DataFrame(data)
    df.to_csv("test.csv")

def to_excel(data: list):
    df = pd.DataFrame(data)
    df.to_excel("test.xlsx")