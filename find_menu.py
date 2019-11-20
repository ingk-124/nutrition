import pulp
import pandas as pd
import numpy as np

full_columns = ['category', 'name', 'R', 'G', 'Y', 'Energy', 'Protein', 'Lipid', 'Carbohydrate', 'Calcium', 'Iron',
                'VitaminA', 'VitaminB1', 'VitaminB2 ', 'VitaminC', 'Salt', 'Vegetables']
file_path = "menu_data.json"

sex = "male"
vec = (2.0, 1.0, 7.0) if sex == "male" else (2.0, 1.0, 4.0)

df = pd.read_json(file_path).T.sort_index()[full_columns]

for i in full_columns[2:]:
    df[i] = df[i].astype("float")

prob = pulp.LpProblem("nutrition", pulp.LpMinimize)
# prob = pulp.LpProblem("nutrition", pulp.LpMaximize)

df["x"] = [pulp.LpVariable("x_" + str(i), lowBound=0, upBound=1, cat=pulp.LpInteger) for i in range(df.shape[0])]  # 1個ずつ
# df["x"] = [pulp.LpVariable("x_" + str(i), lowBound=0, upBound=50, cat=pulp.LpInteger) for i in range(df.shape[0])]  # 50個まで

prob += pulp.lpDot(df.Energy, df.x)  # 目的関数 -> カロリー
# prob += pulp.lpSum(df.x)  # 目的関数 -> 品数

for color, value in zip(["R", "G", "Y"], vec):  # RGY
    prob += pulp.lpDot(df[color], df.x) >= value

# prob += pulp.lpDot(df.Energy, df.x) <= 1500  # カロリー
# prob += pulp.lpDot(df.Protein, df.x) >= 20  # たんぱく質
# prob += pulp.lpDot(df.Calcium, df.x) >= 220  # カルシウム
# prob += pulp.lpDot(df.Iron, df.x) >= 2.5  # 鉄

# must_menu = ["ライスＳ", "１５種類のヘルシーサラダ"]
# for m in df.x[df.name.isin(must_menu)].values:  # must_menuに含まれるメニューを必ず選択する
#     prob += m == 1

# prob += pulp.lpSum(df.x[df["category"] == "ごはん"]) == 1  # ごはんを1品だけ注文する
# prob += pulp.lpSum(df.x[df["category"] == "副菜（小鉢）・汁物"]) >= 2  # 副菜（小鉢）・汁物を2品だけ注文する

# must_category = ["ごはん", "主菜", "副菜（小鉢）・汁物"]
#
# for c in list(set(full_columns) ^ set(must_category)):
#     prob += pulp.lpSum(df.x[df["category"] == c]) == 0
# for c, v in zip(category, (1, 1, 3)):
#     prob += pulp.lpSum(df.x[df["category"] == c]) == v

status = prob.solve()
print(status)

if status == 1:
    df['selector'] = pd.Series([k.value() for k in df.x])

df_selected = df[df["selector"] >= 1]
print(df_selected.drop(["category", "x"], axis=1))
for i in full_columns[2:]:
    print(i, "{0:.1f}".format(np.dot(df_selected[i], df_selected.selector)))
