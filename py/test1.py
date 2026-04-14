def sum_n(y):
    print(f"1 + 2 + ... + {y}的總和是{sum(range(1, y+1))}")


x = int(input("請輸入一個整數："))

if x <= 0:
    print(f"您輸入的值是 {x}, 小於等於0")
else:
    print(f"您輸入的值是 {x}, 大於0")
    for i in range(1, x+1):
        sum_n(i)