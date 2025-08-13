# guess_number.py
import random

# 1〜10のランダムな数字を作る
answer = random.randint(1, 10)

print("1〜10の数字を当ててください！")

# 最大4回までチャレンジ
for attempt in range(4):
    guess = int(input(f"{attempt+1}回目の予想: "))
    
    if guess == answer:
        print("正解！おめでとうございます！")
        break
    elif guess < answer:
        print("もっと大きい数字です。")
    else:
        print("もっと小さい数字です。")
else:
    print(f"残念！正解は {answer} でした。")