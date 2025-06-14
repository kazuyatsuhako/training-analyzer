#!/usr/bin/env python3
from fitparse import FitFile
import pandas as pd
import os
import matplotlib.pyplot as plt

def parse_fit(path):
    # デバッグログ
    print("=== parser.py START ===")
    print("Looking for .fit at:", os.path.abspath(path))
    print("Exists:", os.path.exists(path))

    # .fit 読み込み
    fitfile = FitFile(path)
    records_raw = list(fitfile.get_messages('record'))
    print("Total records:", len(records_raw))
    for rec in records_raw[:3]:
        print({d.name: d.value for d in rec})

    # 必要フィールド抽出
    records = []
    for rec in records_raw:
        records.append({
            'timestamp': rec.get_value('timestamp'),
            'heart_rate': rec.get_value('heart_rate'),
            'speed': rec.get_value('speed'),
            'cadence': rec.get_value('cadence'),
            'power': rec.get_value('power')
        })

    # DataFrame に変換・表示
    df = pd.DataFrame(records)
    print("=== DataFrame head ===")
    print(df.head())

    # 統計情報
    print("=== Stats ===")
    print("Mean heart_rate:", df['heart_rate'].mean())
    print("Mean speed:", df['speed'].mean())

    # 可視化
    df['speed_kmh'] = df['speed'] * 3.6

    plt.figure()
    plt.plot(df['timestamp'], df['heart_rate'])
    plt.xlabel('Timestamp')
    plt.ylabel('Heart Rate')
    plt.title('Heart Rate Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    plt.figure()
    plt.plot(df['timestamp'], df['speed_kmh'])
    plt.xlabel('Timestamp')
    plt.ylabel('Speed (km/h)')
    plt.title('Speed Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # --- A方式: Feedback をここに書く ---
    print("=== Feedback ===")
    target_hr    = float(input("目標平均心拍数 (bpm) を入力してください: "))
    target_speed = float(input("目標平均速度 (km/h) を入力してください: "))
    if df['cadence'].notna().any():
        target_cadence = float(input("目標平均ケイデンス (rpm) を入力してください: "))
    else:
        target_cadence = None

    actual_hr      = df['heart_rate'].mean()
    actual_speed   = df['speed_kmh'].mean()
    actual_cadence = df['cadence'].dropna().mean() if target_cadence is not None else None

    def report(name, actual, target, unit):
        diff   = actual - target
        status = "達成" if diff >= 0 else "未達成"
        print(f"{name}: 実績 {actual:.1f}{unit} / 目標 {target:.1f}{unit} → {status} ({diff:+.1f}{unit})")

    report("平均心拍数",      actual_hr,      target_hr,      "bpm")
    report("平均速度",        actual_speed,   target_speed,   "km/h")
    if target_cadence is not None:
        report("平均ケイデンス", actual_cadence, target_cadence, "rpm")
    # --- Feedback 終了 ---

if __name__ == '__main__':
    parse_fit('data/sample.fit')
