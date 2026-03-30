import os
import matplotlib.pyplot as plt
from data.db_connection import query


def legend_win_rates(output_path: str = "../visuals/legend_win_rates.png"):
    sql = """
    SELECT
        l.name AS legend,
        COUNT(*) AS games_played,
        SUM(CASE WHEN pms.placement = 1 THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN pms.placement = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS win_rate
    FROM PlayerMatchStats pms
    JOIN Legends l ON pms.legend_id = l.legend_id
    GROUP BY l.name
    ORDER BY win_rate DESC;
    """

    df = query(sql)

    if df.empty:
        print("No data returned for legend win rates.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.bar(df["legend"], df["win_rate"], color="purple")
    plt.title("Legend Win Rates")
    plt.ylabel("Win Rate")
    plt.xlabel("Legend")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved legend win rates chart to {output_path}")


if __name__ == "__main__":
    legend_win_rates()
